from databases.constants import Tables
from databases.controller import DatabaseController
from workflows.base_workflow import WorkflowSchema


class WorkflowRepository:
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.WorkflowSchema

    def fetch_by_id(self, workflow_id):
        data = self.db_controller.get(self.table, workflow_id)
        return WorkflowSchema(**data)

    def add_or_update(self, workflow: WorkflowSchema):
        self.db_controller.insert(self.table, workflow.dict(), workflow.id)
