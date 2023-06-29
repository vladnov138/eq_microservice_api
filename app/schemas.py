from pydantic import BaseModel, EmailStr


class UserInSignUp(BaseModel):
    nickname: str
    email: EmailStr
    password: str


class UserInSignIn(BaseModel):
    email: EmailStr
    password: str


class UserInReq(BaseModel):
    token: str

