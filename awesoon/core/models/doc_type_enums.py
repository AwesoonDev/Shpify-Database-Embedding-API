import enum


class DocType(enum.Enum):
    POLICY = "POLICY"
    PRODUCT = "PRODUCT"
    CATEGORY = "CATEGORY"
    PAGE = "PAGE"
    ARTICLE = "ARTICLE"
    BLOG = "BLOG"
    ORDER = "ORDER"


class StorageStatus(enum.Enum):
    ADD = "ADD"
    DELETE = "DELETE"
    IGNORE = "IGNORE"
