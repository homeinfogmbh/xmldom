"""XML data handling"""

from pyxb import RequireValidWhenParsing, RequireValidWhenGenerating
from pyxb.binding.basis import NonElementContent
from pyxb.exceptions_ import PyXBException
from pyxb.utils.domutils import BindingDOMSupport
from xml.dom import Node

__all__ = [
    'validate',
    'any_contents',
    'DisabledValidation']


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
