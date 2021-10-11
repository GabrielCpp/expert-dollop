class RecordNotFound(Exception):
    def __init__(self, message="Record not found"):
        Exception.__init__(self, message)
