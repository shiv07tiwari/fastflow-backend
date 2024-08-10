from databases.controller import DatabaseController


class FileUploadRepository:
    db_controller: DatabaseController

    def __init__(self):
        self.db_controller = DatabaseController()

    def read_file(self, file_path):
        return self.db_controller.get_file_content(file_path)

    def upload_file(self, file_path):
        return self.db_controller.upload_to_firebase(file_path)

    def download_file(self, file_path, destination):
        return self.db_controller.download_file(file_path, destination)
