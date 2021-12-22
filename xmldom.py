"""XML data handling."""

from contextlib import suppress
from multiprocessing import Lock as ProcessLock
from tempfile import NamedTemporaryFile
from threading import Lock as ThreadLock
from typing import Iterator, Optional
from xml.dom import Node

from pyxb import PyXBException
from pyxb import RequireValidWhenParsing
from pyxb import RequireValidWhenGenerating
from pyxb.binding.basis import _Content
from pyxb.binding.basis import complexTypeDefinition
from pyxb.binding.basis import NonElementContent
from pyxb.utils.domutils import BindingDOMSupport


__all__ = [
    'any_contents',
    'dump',
    'strval',
    'validate',
    'DebugDOMErrors',
    'DisabledValidation'
]


BDS = BindingDOMSupport()


def get_string_value(content: _Content) -> str:
    """Returns the string value of the given content."""

    if isinstance(content, NonElementContent):
        return content.value

    if content.elementDeclaration is None:
        if isinstance(content.value, Node):
            return BDS.cloneIntoImplementation(content.value).toxml()

        return content.value.to_dom(BDS).toxml()

    return content.value.toXML()


def any_contents(element: complexTypeDefinition) -> Iterator[str]:
    """Yields stringified contents of xs:any DOMs."""

    for content in element.orderedContent():
        yield get_string_value(content)


def dump(dom: complexTypeDefinition, *, encoding: str = 'utf-8') -> None:
    """Dumps the dom to a temporary file."""

    with NamedTemporaryFile('wb', suffix='.xml', delete=False) as tmp:
        with DisabledValidation():
            tmp.write(dom.toxml(encoding=encoding))

    print('XML dumped to:', tmp.name, flush=True)


def strval(element: Optional[complexTypeDefinition], *,
           sep: str = '') -> Optional[str]:
    """Converts a non-typed DOM element into a string."""

    if element is not None and (content := element.orderedContent()):
        return sep.join(item.value for item in content)

    return None


def validate(binding: complexTypeDefinition) -> bool:
    """Silently validates a class binding."""

    try:
        return binding.validateBinding()
    except PyXBException:
        return False


class DebugDOMErrors:
    """Debugs errors of the given DOM."""

    def __init__(self, dom: complexTypeDefinition, *, encoding: str = 'utf-8'):
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
    """Disables PyXB validation within context."""

    # Locks for thread- and multiprocessing-safety.
    _PROCESS_LOCK = ProcessLock()
    _THREAD_LOCK = ThreadLock()

    def __init__(self, parsing: bool = True, generating: bool = True):
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
        self._PROCESS_LOCK.acquire()
        self._THREAD_LOCK.acquire()
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

        self._PROCESS_LOCK.release()
        self._THREAD_LOCK.release()
