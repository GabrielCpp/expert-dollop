class InvalidUsageError(Exception):
    def __init__(self, message="Invalid usage"):
        Exception.__init__(self, message)
