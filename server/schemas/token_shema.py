from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from uuid import UUID as GUID
from pydantic import Field
from datetime import datetime
from pydantic import BaseModel
from typing import List


class TokenOutput(AuthenticatorModelOutput):

    access_token: str
    expires_in: int
    token_type: str

    class Config:
        schema_extra = {
            'example': {
                'access_token': 'bKiuEzDTKshVON0d1uylewq7owchTrPBT9Eomszpxj5e2buViAEH6hEJJdpIRIe52iiY8S43oe2E2rmSYxB',
                'expires_in': 3600,
                'token_type': 'Bearer'
            }
        }
        orm_mode = True
        arbitrary_types_allowed = True


class DecodedToken(BaseModel):

    guid: str
    name: str
    email: str
    username: str
    roles: List[str]

