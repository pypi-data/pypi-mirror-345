from enum import StrEnum

class MaleoMetadataOrganizationRoleEnums:
    class IdentifierType(StrEnum):
        ID = "id"
        UUID = "uuid"
        KEY = "key"
        NAME = "name"

    class OrganizationRole(StrEnum):
        OWNER = "owner"
        ADMINISTRATOR = "administrator"
        USER = "user"