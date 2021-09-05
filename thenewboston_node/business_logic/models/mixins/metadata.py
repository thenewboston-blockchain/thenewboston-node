from dataclasses import dataclass

from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from .serializable import SerializableMixin


@revert_docstring
@dataclass
@cover_docstring
class MetadataMixin(SerializableMixin):
    pass
