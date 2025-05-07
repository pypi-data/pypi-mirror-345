import uuid

from pydantic import BaseModel


class ClientEnrollment(BaseModel):
    enrollment_key: str
    public_net_key: str
    public_auth_key: str
    preferred_hostname: str
    public_ip: str = None
    interface: str = "nebula1"
    enroll_on_existence: bool = False


class NetworkCreate(BaseModel):
    name: str
    cidr: str


class TemplateCreate(BaseModel):
    name: str
    network_name: str
    is_lighthouse: bool = False
    is_relay: bool = False
    use_relay: bool = True


class NetworkResponse(BaseModel):
    id: int
    name: str
    cidr: str


class TemplateResponse(BaseModel):
    id: int
    name: str
    enrollment_key: uuid.UUID
