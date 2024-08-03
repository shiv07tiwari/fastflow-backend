from databases.constants import Tables
from databases.controller import DatabaseController
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.models.workflow_run import WorkflowRun


class WorkflowRunRepository:
    db_controller: DatabaseController
    table: str
    workflow_node_repo: WorkflowNodeRepository

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.WorkflowRun

    def add_or_update(self, workflow_run: WorkflowRun):
        self.db_controller.insert(self.table, workflow_run.dict(), workflow_run.id)

    def fetch_by_workflow_id(self, workflow_id):
        data = self.db_controller.query_equal(self.table, "workflow_id", workflow_id)
        return [WorkflowRun(**run) for run in data]

    def get(self, run_id):
        data = self.db_controller.get(self.table, run_id)
        return WorkflowRun(**data)
