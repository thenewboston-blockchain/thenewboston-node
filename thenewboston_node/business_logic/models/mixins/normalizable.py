from thenewboston_node.core.utils.cryptography import normalize_dict


class NormalizableMixin:

    def get_normalized(self) -> bytes:
        return normalize_dict(self.serialize_to_dict())  # type: ignore
