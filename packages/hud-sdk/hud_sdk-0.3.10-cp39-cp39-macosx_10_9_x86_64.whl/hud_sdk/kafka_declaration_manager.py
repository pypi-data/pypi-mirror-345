from typing import Dict, List, Optional  # noqa: F401

from ._internal import worker_queue
from .schemas.events import KafkaDeclaration
from .utils import calculate_uuid


class KafkaDeclarationManager:
    def __init__(self) -> None:
        self.declaration_to_id = {}  # type: Dict[str, str]

    def save_kafka_declaration(
        self,
        topic: str,
        group_id: Optional[str],
        pulling_type: str,
        flow_id: Optional[str] = None,
    ) -> str:
        unique_string = self._generate_unique_key(topic, group_id, pulling_type)
        if not flow_id:
            flow_id = str(calculate_uuid(unique_string))

        endpoint_declaration = KafkaDeclaration(flow_id, topic, group_id, pulling_type)
        worker_queue.append(endpoint_declaration)

        self.declaration_to_id[unique_string] = flow_id

        return flow_id

    def get_declaration_id(
        self, topic: str, group_id: Optional[str], pulling_type: str
    ) -> Optional[str]:
        return self.declaration_to_id.get(
            self._generate_unique_key(topic, group_id, pulling_type)
        )

    @staticmethod
    def _generate_unique_key(
        topic: str, group_id: Optional[str], pulling_type: str
    ) -> str:
        return "{}|{}|{}".format(topic, group_id, pulling_type)


class KafkaDeclarationsAggregator:
    def __init__(self) -> None:
        self.declarations = []  # type: List[KafkaDeclaration]

    def add_declaration(self, declaration: KafkaDeclaration) -> None:
        self.declarations.append(declaration)

    def get_and_clear_declarations(self) -> List[KafkaDeclaration]:
        declarations = [declaration for declaration in self.declarations]
        self.clear()
        return declarations

    def clear(self) -> None:
        self.declarations = []
