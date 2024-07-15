import errors

from google.cloud.firestore_v1.base_query import FieldFilter

from databases import base
from databases.constants import QueryOperations

class DatabaseController:
    def __init__(self):
        self.db = base.db
        self.bucket = base.bucket

    def insert(self, table: str, data: dict, document_id: str = None):
        db_collection = self.db.collection(table)
        if id is None:
            db_collection.add(data)
        else:
            db_collection.document(document_id).set(data)
        print("Inserted data in table {}, Data: {}".format(table, data))

    def update(self, table: str, data: dict, document_id: str):
        self.db.collection(table).document(document_id).update(data)

    def delete(self, table: str, document_id: str):
        self.db.collection(table).document(document_id).delete()
        print(f"Deleted document {document_id} from table {table}")

    def get(self, table: str, document_id: str) -> dict:
        data = self.db.collection(table).document(document_id).get()
        if not data.exists:
            raise errors.GenericError(errors.NoRecordFound)
        return data.to_dict()

    def list(self, table: str) -> list:
        docs = self.db.collection(table).stream()
        return [doc.to_dict() for doc in docs]

    def query(self, table: str, key: str, op: str, value) -> list:
        docs = self.db.collection(table).where(filter=FieldFilter(key, op, value)).stream()
        query_results = []
        for doc in docs:
            query_results.append(doc.to_dict())
        return query_results

    def query_equal(self, table: str, key: str, value) -> list:
        return self.query(table, key, QueryOperations.Equals, value)

    def query_in(self, table: str, key: str, value) -> list:
        return self.query(table, key, QueryOperations.In, value)

    def clear_table(self, table: str):
        """
        Clears all entries from the specified table.

        :param table: The name of the table to clear
        """
        batch_size = 100  # Firestore recommends deleting in batches
        docs = self.db.collection(table).limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            # If we have deleted a number of documents equal to the batch size,
            # there might be more documents to delete, so we recursively call
            # the function again
            self.clear_table(table)

        print(f"Cleared {deleted} documents from table {table}")

    def get_file_content(self, file_path: str):
        try:
            blob = self.bucket.blob(file_path)
            file_bytes = blob.download_as_bytes()
            return file_bytes
        except Exception as e:
            print(f"Error downloading file: {e}")
            raise Exception("Failed to download file from Firebase Storage")

