class Result():
    def __init__(self, data=None, error: Exception = None):
        self.data = data
        self.error = error

    @property
    def is_success(self):
        return self.error is None

    @property
    def is_failure(self):
        return self.error is not None

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Result):
            return self.data == __o.data and type(self.error) == type(__o.error)
        return False

    def __hash__(self) -> int:
        return hash((self.data, self.error))

    def __str__(self) -> str:
        return f"Result(data={self.data}, error={self.error})"

    def __repr__(self) -> str:
        return f"Result(data={self.data}, error={self.error})"
