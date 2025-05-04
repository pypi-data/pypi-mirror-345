from ...models.utils.types import StrObjectId
from ...models.company.assets.users.user import User, UserRole, AgentBusinessAreaAssignment, FunnelAssignment, AssetPermission, UserType
from typing import Optional, List, Dict
from ...models.company.assets.company_assets import CompanyAssetType
from ...models.company.assets.users.user_asset_permission import Permission
from ...models.forms.company.auth0_company_registration_form import Auth0CompanyRegistrationForm
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ...models.company.assets.users.user_asset_permission import FunnelAssignmentRequest, AgentBusinessAreaAssignmentRequest
class UserFactory:

    @staticmethod
    def instantiate_user(user_dict: dict) -> User:
        return User(**user_dict)

    @staticmethod
    def create_root_user(email:str, name:str, company_id:StrObjectId)-> User:
        user = UserFactory.create_admin(company_id=company_id, email=email, name=name)
        user.is_root = True
        user = UserFactory.add_role(user=user, role=UserRole.SUPER_ADMIN)
        return user

    @staticmethod
    def create_agent(company_id: StrObjectId, email: str, name: str, phone_number: Optional[str] = None, business_areas: Optional[List[AgentBusinessAreaAssignmentRequest]] = None, funnels: Optional[List[FunnelAssignmentRequest]] = None):
        now = datetime.now(tz=ZoneInfo("UTC"))
        default_permissions = [
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TAGS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.PRODUCTS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SALES, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FUNNELS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.BUSINESS_AREAS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SOURCES, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TEMPLATES, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FAST_ANSWERS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.ANALYTICS, permission=Permission.USE, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.USERS, permission=Permission.USE, all_assets=True),
        ]
        business_areas_assignments = []
        funnels_assignments = []
        if business_areas:
            for business_area_assignment in business_areas:
                business_areas_assignments.append(AgentBusinessAreaAssignment.create_from_request(business_area_assignment))
        if funnels:
            for funnel_assignment in funnels:
                funnels_assignments.append(FunnelAssignment.create_from_request(funnel_assignment))

        user = User(
            company_id=company_id,
            email=email,
            name=name,
            phone_number=phone_number,
            roles=[UserRole.AGENT],
            asset_permissions=default_permissions,
            created_at=now,
            updated_at=now,
            business_areas=business_areas_assignments,
            funnels=funnels_assignments
        )

        return user

    @staticmethod
    def create_admin(company_id: StrObjectId, email: str, name: str, phone_number: Optional[str] = None) -> User:
        """Create a new user with the ADMIN role"""
        default_permissions = [
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TAGS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.PRODUCTS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SALES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FUNNELS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.BUSINESS_AREAS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SOURCES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TEMPLATES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FAST_ANSWERS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.ANALYTICS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.USERS, permission=Permission.ADMIN, all_assets=True),
        ]
        now = datetime.now(tz=ZoneInfo("UTC"))
        user = User(
            company_id=company_id,
            email=email,
            name=name,
            phone_number=phone_number,
            roles=[UserRole.ADMIN],
            can_view_other_user_chats=True,
            asset_permissions=default_permissions,
            created_at=now,
            updated_at=now
        )
        return user

    @staticmethod
    def add_role(user: User, role: UserRole) -> User:
        """Add a role to this user"""
        if role not in user.roles:
            user.roles.append(role)
        return user

    @staticmethod
    def create_integration_user(
        name: str,
        company_id: StrObjectId,
        description: str,
        roles: List[UserRole],
        permissions: Optional[List[AssetPermission]] = None,
        expiry_days: Optional[int] = 365,  # Default to 1 year
        business_areas: Optional[List[AgentBusinessAreaAssignmentRequest]] = None,
        funnels: Optional[List[FunnelAssignmentRequest]] = None,
    ) -> User:
        """Create a new integration user with an API key"""
        default_permissions = [
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TAGS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.PRODUCTS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SALES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FUNNELS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.BUSINESS_AREAS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.SOURCES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.TEMPLATES, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.FAST_ANSWERS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.ANALYTICS, permission=Permission.ADMIN, all_assets=True),
            AssetPermission.default_for_type(asset_type=CompanyAssetType.USERS, permission=Permission.ADMIN, all_assets=True),
        ]
        now = datetime.now(tz=ZoneInfo("UTC"))

        business_areas_assignments = []
        funnels_assignments = []
        if business_areas:
            for business_area_assignment in business_areas:
                business_areas_assignments.append(AgentBusinessAreaAssignment.create_from_request(AgentBusinessAreaAssignmentRequest(**business_area_assignment)))  #type: ignore
        if funnels:
            for funnel_assignment in funnels:
                funnels_assignments.append(FunnelAssignment.create_from_request(FunnelAssignmentRequest(**funnel_assignment)))  #type: ignore

        if expiry_days:
            expires_at = datetime.now(tz=ZoneInfo("UTC")) + timedelta(days=expiry_days)
        else:
            expires_at = None

        # Create the user without an API key first
        integration_user = User(
            name=name,
            company_id=company_id,
            user_type=UserType.INTEGRATION,
            roles=roles,
            asset_permissions=default_permissions if permissions is None else permissions,
            api_key_description=description,
            created_at=now,
            updated_at=now,
            business_areas=business_areas_assignments,
            funnels=funnels_assignments,
            api_key_expires_at=expires_at
        )

        return integration_user
