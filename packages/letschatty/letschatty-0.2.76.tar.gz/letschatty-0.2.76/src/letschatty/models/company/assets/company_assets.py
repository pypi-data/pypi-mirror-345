from enum import StrEnum


class CompanyAssetType(StrEnum):
    USERS = "users"
    BUSINESS_AREAS = "business_areas"
    FUNNELS = "funnels"
    PRODUCTS = "products"
    SALES = "sales"
    TAGS = "tags"
    SOURCES = "sources"
    TEMPLATES = "templates"
    FAST_ANSWERS = "fast_answers"
    ANALYTICS = "analytics"
    CHATS = "chats"
    TOPICS = "topics"
    COMPANY = "company"