from dataclasses import dataclass
from itertools import chain

from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from .serializable import SerializableMixin


@revert_docstring
@dataclass
@cover_docstring
class MetadataMixin(SerializableMixin):

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        if 'meta' not in exclude:
            exclude = tuple(chain(exclude, ('meta',)))

        return super().serialize_to_dict(
            skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types, exclude=exclude
        )
