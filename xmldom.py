"""XML data handling."""

from contextlib import suppress
from tempfile import NamedTemporaryFile
from xml.dom import Node

from pyxb import PyXBException
from pyxb import RequireValidWhenParsing
from pyxb import RequireValidWhenGenerating
from pyxb.binding.basis import NonElementContent
from pyxb.utils.domutils import BindingDOMSupport


__all__ = [
    'any_contents',
    'dump',
    'strval',
    'validate',
    'DebugDOMErrors',
    'DisabledValidation']


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


def dump(dom, encoding='utf-8'):
    """Dumps the dom to a temporary file."""

    with NamedTemporaryFile('wb', suffix='.xml', delete=False) as tmp:
        with DisabledValidation():
            tmp.write(dom.toxml(encoding=encoding))

    print('XML dumped to:', tmp.name, flush=True)


def strval(element, sep=''):
    """Converts a non-typed DOM element into a string."""

    if element is not None and element.orderedContent():
        return sep.join(item.value for item in element.orderedContent())

    return None


def validate(binding):
    """Silently validates a class binding."""

    try:
        return binding.validateBinding()
    except PyXBException:
        return False


class DebugDOMErrors:
    """Debugs errors of the given DOM."""

    def __init__(self, dom, encoding='utf-8'):
        """Sets the DOM."""
        self.dom = dom
        self.encoding = encoding

    def __enter__(self):
        """Enters a context."""
        return self

    def __exit__(self, typ, value, traceback):
        """Dumps the DOM on errors."""
        if isinstance(value, PyXBException):
            dump(self.dom, encoding=self.encoding)

            with suppress(AttributeError):
                print('Exceptions details:', value.details())


class DisabledValidation:
    """Disables PyXB validation within context.

    This is NOT thread-safe!
    """

    def __init__(self, parsing=True, generating=True):
        """Sets the disabled validation for parsing and / or generating.
        Defaults to disable validation (True) on both.
        The respective option will not be changed if it is set to None.
        """
        self.parsing = parsing
        self.generating = generating
        self.require_valid_when_parsing = RequireValidWhenParsing()
        self.require_valid_when_generating = RequireValidWhenGenerating()

    def __enter__(self):
        """Disable validation."""
        self.require_valid_when_parsing = RequireValidWhenParsing()
        self.require_valid_when_generating = RequireValidWhenGenerating()

        if self.parsing is not None:
            RequireValidWhenParsing(not self.parsing)

        if self.generating is not None:
            RequireValidWhenGenerating(not self.generating)

        return self

    def __exit__(self, *_):
        """Re-enables validation."""
        if self.parsing is not None:
            RequireValidWhenParsing(self.require_valid_when_parsing)

        if self.generating is not None:
            RequireValidWhenGenerating(self.require_valid_when_generating)
