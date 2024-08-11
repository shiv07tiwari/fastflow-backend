from pydantic import BaseModel


class GoogleUser(BaseModel):
    email: str
    code: str
    access_token: str
    refresh_token: str
    name: str

    def to_dict(self):
        return self.__dict__
