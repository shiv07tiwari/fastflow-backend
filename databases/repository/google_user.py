from databases.constants import Tables
from databases.controller import DatabaseController


class GoogleUserRepository:
    db_controller: DatabaseController
    table: str

    def __init__(self):
        self.db_controller = DatabaseController()
        self.table = Tables.GoogleUser

    def add_or_update(self, email, data):
        self.db_controller.insert(self.table, data, email)

    def get(self, email):
        return self.db_controller.get(self.table, email)