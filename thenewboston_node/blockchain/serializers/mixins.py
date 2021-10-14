from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.settings import api_settings

from thenewboston_node.business_logic.exceptions import ValidationError


class BaseDataclassSerializerMixin:

    def _get_dataclass(self):
        if self.dataclass:
            return self.dataclass
        else:
            return self.Meta.dataclass


class DataclassDeserializeMixin(BaseDataclassSerializerMixin):

    def to_internal_value(self, data):
        try:
            return self._get_dataclass().deserialize_from_dict(data)
        except ValidationError as ex:
            raise DRFValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(ex)]})


class DataclassSerializeMixin(BaseDataclassSerializerMixin):

    def to_representation(self, instance):
        return instance.serialize_to_dict()
