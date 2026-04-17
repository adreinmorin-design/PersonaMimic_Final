from pydantic import BaseModel


class ModelUpdate(BaseModel):
    model: str


class CloudUpdate(BaseModel):
    use_cloud: bool


class VaultEntry(BaseModel):
    key: str
    value: str
    encrypt: bool = True


class SystemHealth(BaseModel):
    status: str
    model: str
    cloud: bool
