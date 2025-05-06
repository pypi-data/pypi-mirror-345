from typing import Optional, List, Any, ClassVar
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, model_validator, field_validator
from enum import StrEnum
from ....base_models import CompanyAssetModel, ChattyAssetPreview
from ...notifications.notification import Notification, WhatsAppNotifications
from .user_asset_permission import AssetPermission, AgentBusinessAreaAssignment, FunnelAssignment

class UserRole(StrEnum):
    AGENT = "agent"           # Can handle chats at a specific business area and funnel
    SUPER_AGENT = "super_agent" # Can handle chats at any business area and funnel
    OVERVIEWER = "overviewer" # Can view chats but not interact
    MARKETER = "marketer"     # Can manage certain assets
    ADMIN = "admin"           # Can administer users and assets
    SUPER_ADMIN = "super_admin" # Can administer everything

class UserType(StrEnum):
    HUMAN = "human"
    INTEGRATION = "integration"

class UserStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"

class UserPreview(ChattyAssetPreview):
    status: UserStatus
    last_activity_timestamp: datetime

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        projection = super().get_projection()
        projection["status"] = 1
        projection["last_activity_timestamp"] = 1
        return projection

class User(CompanyAssetModel):
    """
    Unified user model combining multiple possible roles.
    Different fields become relevant based on the roles a user has.
    """
    # Basic info
    user_type: UserType = Field(default=UserType.HUMAN)
    name: str
    email: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)

    # Status and activity
    status: UserStatus = Field(default=UserStatus.ONLINE)
    last_activity_timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=ZoneInfo("UTC")))

    # Roles and permissions
    roles: List[UserRole] = Field(default_factory=list)
    is_root: bool = Field(default=False, description="If true, root user can't be deleted and has super admin powers")

    # Asset permissions (applies to all users)
    asset_permissions: List[AssetPermission] = Field(default_factory=list, description="Asset permissions for the user")

    # Chat visibility (for non-agents who need to see chats)
    can_view_other_user_chats: bool = Field(default=False, description="If true, the user can view other users' chats")

    # Notifications
    notifications: List[Notification] = Field(default_factory=list)
    whatsapp_notification: WhatsAppNotifications = Field(default_factory=WhatsAppNotifications.default)

    # Agent specific fields
    business_areas: List[AgentBusinessAreaAssignment] = Field(default_factory=list)
    funnels: List[FunnelAssignment] = Field(default_factory=list)
    auto_assign_chats: bool = Field(default=False)
    preview_class: ClassVar[type[UserPreview]] = UserPreview

    # API key fields
    api_key_hash: Optional[str] = Field(default=None)  # Stored hashed, not plaintext
    api_key_created_at: Optional[datetime] = Field(default=None)
    api_key_expires_at: Optional[datetime] = Field(default=None)
    api_key_last_used_at: Optional[datetime] = Field(default=None)
    api_key_description: Optional[str] = Field(default=None)

    @property
    def is_admin(self) -> bool:
        return UserRole.ADMIN in self.roles or UserRole.SUPER_ADMIN in self.roles or self.is_root

    @property
    def is_super_admin(self) -> bool:
        return UserRole.SUPER_ADMIN in self.roles or self.is_root

    @property
    def is_agent(self) -> bool:
        return UserRole.AGENT in self.roles

    @property
    def is_marketer(self) -> bool:
        return UserRole.MARKETER in self.roles

    @property
    def is_overviewer(self) -> bool:
        return UserRole.OVERVIEWER in self.roles

    @property
    def is_integration(self) -> bool:
        return self.user_type == UserType.INTEGRATION

    @model_validator(mode="before")
    @classmethod
    def validate_email(cls, data: Any) -> Any:
        if data.get("user_type") == UserType.HUMAN and not data.get("email"):
            raise ValueError("Email is required for human users")
        return data

    @field_validator("api_key_expires_at", mode="after")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v is None:
            return v
        return v.replace(tzinfo=ZoneInfo("UTC")) if v.tzinfo is None else v.astimezone(ZoneInfo("UTC"))
