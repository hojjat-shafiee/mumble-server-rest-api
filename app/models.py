from pydantic import BaseModel, Field
from typing import Optional, Any


class ServerModel(BaseModel):
    """Configuration model for creating a new virtual server."""
    password: Optional[str] = Field(None, description="Server password")
    port: Optional[int] = Field(None, description="Server listening port")
    timeout: Optional[str] = Field(None, description="Client connection timeout in seconds")
    bandwidth: Optional[int] = Field(None, description="Max allowed bandwidth in bits per second")
    users: Optional[int] = Field(None, description="Maximum concurrent users")
    welcomeText: Optional[str] = Field(None, description="Welcome message displayed on connect")
    registerName: Optional[str] = Field(None, description="Server name shown in public server list")


class ServerUpdateModel(BaseModel):
    """Configuration model for updating an existing virtual server's settings."""
    password: Optional[str] = Field(None, description="Server password")
    timeout: Optional[str] = Field(None, description="Client connection timeout in seconds")
    bandwidth: Optional[int] = Field(None, description="Max allowed bandwidth in bits per second")
    users: Optional[int] = Field(None, description="Maximum concurrent users")
    welcomeText: Optional[str] = Field(None, description="Welcome message displayed on connect")
    registerName: Optional[str] = Field(None, description="Server name shown in public server list")


class MessageResponse(BaseModel):
    message: str


class ServerSummaryResponse(BaseModel):
    id: int
    name: str
    address: str
    host: str
    port: int
    running: bool
    users: int
    maxusers: int
    channels: int
    uptime_seconds: int
    uptime: str
    log_length: int


class ServerDetailResponse(BaseModel):
    id: int
    name: str
    host: str
    port: int
    address: str
    password: Optional[str] = None
    welcometext: str
    user_count: int
    maxusers: int
    running: bool
    uptime: int
    humanize_uptime: str
    parent_channel: Optional[Any] = None
    sub_channels: Optional[Any] = None
    users: Optional[Any] = None
    registered_users: Optional[Any] = None
    log_length: int


class ServerLogEntry(BaseModel):
    message: str
    timestamp: int


class HealthResponse(BaseModel):
    status: str
    connected: bool
    murmur_version: Optional[str] = None
    error: Optional[str] = None
