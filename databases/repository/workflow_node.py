from typing import List

from databases import base
from databases.constants import QueryConstants, Tables
from databases.controller import DatabaseController
from workflows.workflow_node import WorkFlowNode


class WorkflowNodeRepository:
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController(base.db)
        self.table = Tables.WorkFlowNode

    def fetch_workflow_nodes_by_workflow_id(self, workflow_id) -> List[WorkFlowNode]:
        nodes_data = self.db_controller.query_equal(self.table, QueryConstants.Node, workflow_id)
        nodes = []
        for node in nodes_data:
            nodes.append(WorkFlowNode(**node))
        return nodes
