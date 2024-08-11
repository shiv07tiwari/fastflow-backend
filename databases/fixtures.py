from databases.constants import Tables, NodeTypeClassMappings
from databases.controller import DatabaseController


class Fixtures:
    def __init__(self):
        self.db_controller = DatabaseController()

    def add_test_data(self, n: int = 1):
        existing_nodes = [node.get("id") for node in self.db_controller.list(Tables.Node)]
        self.db_controller.clear_table(Tables.Node)
        new_nodes = NodeTypeClassMappings.keys()
        for node in new_nodes:
            if node not in existing_nodes:
                node_data = NodeTypeClassMappings.get(node)()
                node_data.inputs = [input.to_dict() for input in node_data.inputs]
                self.db_controller.insert(Tables.Node, node_data.to_dict(), document_id=node)

        self.db_controller.clear_table(Tables.WorkflowRun)