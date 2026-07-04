from pydantic import BaseModel, EmailStr, Field

# ── User ──────────────────────────────────────────────────────────────────────


class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


# ── Auth ──────────────────────────────────────────────────────────────────────


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Note ──────────────────────────────────────────────────────────────────────


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="")


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None


class NoteOut(BaseModel):
    id: int
    title: str
    body: str
    user_id: int

    model_config = {"from_attributes": True}
