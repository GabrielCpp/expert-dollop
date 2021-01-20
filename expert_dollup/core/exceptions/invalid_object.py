class InvalidObject(Exception):
    def __init__(self, exception_id: str, detailed_error: str):
        Exception.__init__(self, detailed_error)
        self.exception_id = exception_id
        self.detailed_error = detailed_error
