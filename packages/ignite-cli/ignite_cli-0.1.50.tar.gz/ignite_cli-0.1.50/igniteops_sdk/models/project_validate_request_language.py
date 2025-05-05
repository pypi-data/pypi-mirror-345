from enum import Enum


class ProjectValidateRequestLanguage(str, Enum):
    GOLANG = "golang"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    VALUE_4 = ".net"

    def __str__(self) -> str:
        return str(self.value)
