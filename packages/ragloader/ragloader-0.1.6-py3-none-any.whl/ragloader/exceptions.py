class QdrantCollectionExists(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidConfigPath(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidConfigStructure(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ParserNotFound(Exception):
    def __init__(self, message: str):
        super().__init__(message)
