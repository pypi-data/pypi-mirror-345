from typing import Optional

from docdeid.document import Document
from docdeid.process.doc_processor import DocProcessorGroup
from docdeid.tokenizer import Tokenizer


class DocDeid:  # pylint: disable=R0903
    """
    The main class used for de-identifying text.

    This class contains one or more
    document processors in a :class:`.DocProcessorGroup`, which can be modified
    directly in :attr:`DocDeid.processors`. Additionally, it stores and passes any
    number of tokenizers in the :attr:`DocDeid.tokenizers` dictionary, also directly
    accessible.
    """

    def __init__(self) -> None:
        self.tokenizers: dict[str, Tokenizer] = {}
        """
        A dictionary of named :class:`.Tokenizer`, that are passed to the
        :class:`.Document` object.

        If there is only one tokenizer, you may add it with the `default` key, so
        that it will be used when the :meth:`.Document.get_tokens` method is called
        without a tokenizer name.
        """

        self.processors: DocProcessorGroup = DocProcessorGroup()
        """
        The processors of this deidentifier, captured in a :class:`.DocProcessorGroup`.

        Processors can be added or modified by interacting with this attribute directly.
        """

    def deidentify(
        self,
        text: str,
        enabled: Optional[set[str]] = None,
        disabled: Optional[set[str]] = None,
        metadata: Optional[dict] = None,
    ) -> Document:
        """
        Main interface to de-identifying text.

        Args:
            text: The input text, that needs de-identification.
            enabled: A set of processors names that should be executed for this text.
                Cannot be used with `disabled`.
            disabled: A set of processors names that should not be executed for this
                text. Cannot be used with `enabled`.
            metadata: A dictionary containing additional information on this text,
                that is accessible to processors.

        Returns:
            A :class:`.Document` with the relevant information (e.g.
            :attr:`.Document.annotations`, :attr:`.Document.deidentified_text`).
        """

        doc = Document(text, tokenizers=self.tokenizers, metadata=metadata)
        self.processors.process(doc, enabled=enabled, disabled=disabled)

        return doc
