class YNABError(Exception):
    pass


class YNABNotFoundError(YNABError):
    def __init__(self, object: str) -> None:
        self.object = object

    def __str__(self) -> str:
        return f'"{self.object}" does not exist'
