from databases import base
from databases.constants import Tables, NodeTypeClassMappings
from databases.controller import DatabaseController
from nodes.base_node import Node


class NodeRepository:
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController(base.db)
        self.table = Tables.Node

    def fetch_by_id(self, node_id: str) -> Node:
        data = self.db_controller.get(Tables.Node, node_id)
        node_class = NodeTypeClassMappings[data['workflow_node_type']]
        return node_class(**data)
