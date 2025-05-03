# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
from enum import Enum


class IAMUnitType(Enum):
    GROUPS = "groups"
    ROLES = "roles"
    PERMISSIONS = "permissions"

    def __str__(self):
        return self.value


class IAMAction(Enum):
    ALLOW="allow"
    DENY="deny"
    GRANT="grant"
    REVOKE="revoke"

class IAMUserType(Enum):
    ANONYMOUS="anonymous"
    AUTHENTICATED="authenticated"
    CUSTOMER="customer"
    EXTERNAL="external"
    PARTNER="partner"
    INTERNAL="internal"
    EMPLOYEE="employee"
    SYSTEM="system"
    ADMIN="admin"
    SUPERADMIN="superadmin"
