from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.settings import api_settings
from rest_framework_dataclasses.serializers import DataclassSerializer

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest


class NodeDeclarationSignedChangeRequestSerializer(DataclassSerializer):

    class Meta:
        dataclass = NodeDeclarationSignedChangeRequest

    def to_internal_value(self, data):
        try:
            return NodeDeclarationSignedChangeRequest.deserialize_from_dict(data)
        except ValidationError as ex:
            raise DRFValidationError({api_settings.NON_FIELD_ERRORS_KEY: [str(ex)]})
