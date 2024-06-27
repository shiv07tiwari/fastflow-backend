class DatabaseController:
    def __init__(self, db):
        self.db = db

    def insert(self, table: str, data: dict):
        self.db.collection(table).add(data)
        print("Inserted data in table {}, Data: {}".format(table, data))
