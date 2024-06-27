class GenericError(Exception):
    code: str
    message: str

    def __init__(self, error_dict: dict):
        self.code = error_dict["code"]
        self.message = error_dict["message"]


NoRecordFound = {
    "code": "E001",
    "message": "No records found."
}
