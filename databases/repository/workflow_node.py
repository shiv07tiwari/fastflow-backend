from typing import List

from databases import base
from databases.constants import QueryConstants, Tables
from databases.controller import DatabaseController
from workflows.workflow_node import WorkFlowNode


class WorkflowNodeRepository:
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.WorkFlowNode

    def fetch_all_by_workflow_id(self, workflow_id) -> List[WorkFlowNode]:
        nodes_data = self.db_controller.query_equal(self.table, QueryConstants.Workflow, workflow_id)
        nodes = []
        for node in nodes_data:
            nodes.append(WorkFlowNode(**node))
        return nodes

    def fetch_by_id(self, node_id) -> WorkFlowNode:
        node_dict = self.db_controller.get(self.table, node_id)
        return WorkFlowNode(**node_dict)

    def add_or_update(self, node_id, data):
        # Data contains external_inputs, internal_inputs, common_inputs
        # Convert them to dict
        data['external_inputs'] = [input.to_dict() for input in data['external_inputs']]
        data['internal_inputs'] = [input.to_dict() for input in data['internal_inputs']]
        data['common_inputs'] = [input.to_dict() for input in data['common_inputs']]
        self.db_controller.insert(self.table, data, node_id)

    def delete(self, node_id):
        self.db_controller.delete(self.table, node_id)
