from databases.constants import Tables, NodeTypeClassMappings
from databases.controller import DatabaseController
from nodes.base_node import BaseNode


class NodeRepository:
    """
    This is BaseNode Repository. TODO: Rename to BaseNodeRepository
    """
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.Node

    def fetch_by_id(self, node_id: str) -> BaseNode:
        data = self.db_controller.get(Tables.Node, node_id)
        node_class = NodeTypeClassMappings[data['id']]
        return node_class(**data)

    def fetch_all(self) -> list[BaseNode]:
        data = self.db_controller.list(Tables.Node)
        return [NodeTypeClassMappings[node['id']](**node) for node in data]


