"""XML data handling."""

from xml.dom import Node

from pyxb import PyXBException, RequireValidWhenParsing, \
    RequireValidWhenGenerating
from pyxb.binding.basis import NonElementContent
from pyxb.utils.domutils import BindingDOMSupport

__all__ = [
    'validate',
    'any_contents',
    'DisabledValidation']


def validate(binding):
    """Silently validates a class binding."""

    try:
        return binding.validateBinding()
    except PyXBException:
        return False


def any_contents(dom, bds=None):
    """Yields stringified contents of xs:any DOMs."""

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
    """Disables PyXB validation within context.

    This is NOT thread-safe!
    """

    def __init__(self, parsing=True, generating=True):
        """Sets the disabled validation for parsing and / or generating.
        Defaults to disable validation (True) on both.
        """
        self.parsing = parsing
        self.generating = generating
        self.require_valid_when_parsing = RequireValidWhenParsing()
        self.require_valid_when_generating = RequireValidWhenGenerating()

    def __enter__(self):
        """Disable validation."""
        self.require_valid_when_parsing = RequireValidWhenParsing()
        self.require_valid_when_generating = RequireValidWhenGenerating()
        RequireValidWhenParsing(not self.parsing)
        RequireValidWhenGenerating(not self.generating)
        return self

    def __exit__(self, *_):
        """Re-enables validation."""
        RequireValidWhenParsing(self.require_valid_when_parsing)
        RequireValidWhenGenerating(self.require_valid_when_generating)
