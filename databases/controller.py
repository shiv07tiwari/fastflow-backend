import errors


class DatabaseController:
    def __init__(self, db):
        self.db = db

    def insert(self, table: str, data: dict, document_id: str = None):
        db_collection = self.db.collection(table)
        if id is None:
            db_collection.add(data)
        else:
            if db_collection.document(document_id).get().exists:
                print("Entry already exists! DocumentId: {}".format(document_id))
                return
            else:
                db_collection.document(document_id).set(data)
        print("Inserted data in table {}, Data: {}".format(table, data))

    def update(self, table: str, data: dict, document_id: str):
        self.db.collection(table).document(document_id).update(data)

    def get(self, table: str, document_id: str) -> dict:
        data = self.db.collection(table).document(document_id).get()
        if not data.exists:
            raise errors.GenericError(errors.NoRecordFound)
        return data.to_dict()
