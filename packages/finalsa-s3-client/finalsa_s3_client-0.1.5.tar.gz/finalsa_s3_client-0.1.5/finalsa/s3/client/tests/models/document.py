from pydantic import BaseModel


class Document(BaseModel):

    value: bytes
    content_type: str
