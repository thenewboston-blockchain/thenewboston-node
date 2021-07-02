from dataclasses import dataclass

from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from .mixins.compactable import CompactableMixin
from .mixins.documentable import DocumentableMixin
from .mixins.misc import HumanizedClassNameMixin


@revert_docstring
@dataclass
@cover_docstring
class BaseDataclass(CompactableMixin, HumanizedClassNameMixin, DocumentableMixin):
    pass
