from databases.constants import Tables, NodeTypeClassMappings
from databases.controller import DatabaseController


class Fixtures:
    def __init__(self):
        self.db_controller = DatabaseController()

    def add_test_data(self, n: int = 1):
        self.db_controller.clear_table(Tables.Node)
        for _node in NodeTypeClassMappings.values():
            node = _node()
            node.inputs = [input.to_dict() for input in node.inputs]
            self.db_controller.insert(Tables.Node, node.to_dict(), document_id=node.id)

        self.db_controller.clear_table(Tables.WorkflowRun)
