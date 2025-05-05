from enum import Enum


class IntegrationRepositoryCreateRequestAccountType(str, Enum):
    ORGANIZATION = "organization"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
