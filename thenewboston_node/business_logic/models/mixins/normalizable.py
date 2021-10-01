from thenewboston_node.core.utils.cryptography import normalize_dict


# TODO(dmu) HIGH: Do we still need NormalizableMixin?
class NormalizableMixin:

    def get_normalized_for_cryptography(self) -> bytes:
        return normalize_dict(self.serialize_to_dict())  # type: ignore
