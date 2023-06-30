import enum


class DocType(enum.Enum):
    POLICY = "POLICY"
    PRODUCT = "PRODUCT"
    CATEGORY = "CATEGORY"


class StorageStatus(enum.Enum):
    ADD = "ADD"
    DELETE = "DELETE"
    IGNORE = "IGNORE"
