from databases import base
from databases.constants import Tables
from databases.controller import DatabaseController
from databases.repository.workflow_node import WorkflowNodeRepository
from workflows.base_workflow import WorkflowSchema


class WorkflowRepository:
    db_controller: DatabaseController
    table: str
    workflow_node_repo: WorkflowNodeRepository

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.WorkflowSchema
        self.workflow_node_repo = WorkflowNodeRepository()

    def fetch_by_id(self, workflow_id):
        data = self.db_controller.get(self.table, workflow_id)
        return WorkflowSchema(**data)
