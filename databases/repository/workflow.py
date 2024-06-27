from databases import base
from databases.controller import DatabaseController


class WorkflowRepository:
    db_controller: DatabaseController

    def __init__(self):
        self.db_controller = DatabaseController(base.db)
