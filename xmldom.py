"""XML data handling"""

from pyxb import RequireValidWhenParsing, RequireValidWhenGenerating
from pyxb.binding.basis import NonElementContent
from pyxb.binding.content import _PluralBinding
from pyxb.exceptions_ import PyXBException
from pyxb.utils.domutils import BindingDOMSupport
from xml.dom import Node

__all__ = [
    'DOMWalkTrip',
    'validate',
    'any_contents',
    'DisabledValidation',
    'DOMWalker']


class DOMWalkTrip(Exception):
    """Indicates that the DOMWalker tripped while walking"""

    pass


def validate(binding):
    """Silently validates a class binding"""

    try:
        result = binding.validateBinding()
    except PyXBException:
        return False
    else:
        return result


def any_contents(dom, bds=None):
    """Yields stringified contents of xs:any DOMs"""

    for element in dom.orderedContent():
        if isinstance(element, NonElementContent):
            yield element.value
        elif element.elementDeclaration is None:
            bds = BindingDOMSupport() if bds is None else bds

            if isinstance(element.value, Node):
                yield bds.cloneIntoImplementation(element.value).toxml()
            else:
                yield element.value.to_dom(bds).toxml()
        else:
            yield element.value.toXML()


class DisabledValidation():
    """Disables PyXB validation within context

    XXX: This is NOT thread-safe!
    """

    def __init__(self, parsing=True, generating=True):
        """Sets the disabled validation for parsing and / or generating.
        Defaults to disable validation (True) on both.
        """
        self.parsing = parsing
        self.generating = generating

    def __enter__(self):
        """Disable validation"""
        self.require_valid_when_parsing = RequireValidWhenParsing()
        self.require_valid_when_generating = RequireValidWhenGenerating()
        RequireValidWhenParsing(not self.parsing)
        RequireValidWhenGenerating(not self.generating)
        return self

    def __exit__(self, *_):
        """Re-enables validation"""
        RequireValidWhenParsing(self.require_valid_when_parsing)
        RequireValidWhenGenerating(self.require_valid_when_generating)


class DOMWalker():
    """Walks DOM nodes"""

    def __init__(self, root, sep='/'):
        """Sets the root node and path separator"""
        self._root = root
        self._sep = sep

    def __call__(self, path, ident_sep='='):
        """Get the path"""
        self._walked = ['']
        root = self._root

        for node in path.split(self._sep):
            if not node:
                # Skip empty nodes
                continue

            if isinstance(root, _PluralBinding):
                # Try to get plural binding element by index
                try:
                    i = int(node)
                except ValueError:
                    # Try to get plural binding element by identifier
                    try:
                        ident, value = node.split(ident_sep)
                    except ValueError:
                        raise DOMWalkTrip(
                            'Expected index or identification at "{}" '
                            'but got "{}"'.format(self.walked, node))
                    else:
                        for elem in root:
                            try:
                                ident_ = getattr(elem, ident)
                            except AttributeError:
                                raise DOMWalkTrip(
                                    'Elements at {} cannot be identified by '
                                    '{}'.format(self.walked, ident))
                            else:
                                if ident_ == value:
                                    break
                        else:
                            raise DOMWalkTrip(
                                'Item at {} not found for identifier '
                                '{}'.format(self.walked, ident))

                        root = elem
                        self._walked.append(node)
                else:
                    try:
                        root = root[i]
                    except IndexError:
                        raise DOMWalkTrip(
                            'Index "{}" out of bounds at {}'.format(
                                i, self.walked))
                    else:
                        self._walked.append(node)
            else:
                try:
                    root = getattr(root, node)
                except AttributeError:
                    raise DOMWalkTrip(
                        'No such sub-node: {} at {}'.format(
                            node, self.walked))
                else:
                    self._walked.append(node)

        return root

    @property
    def walked(self):
        """Returns the walked path"""
        try:
            walked = self._walked
        except AttributeError:
            raise DOMWalkTrip('Did not walk yet')
        else:
            return self._sep.join(walked)
