class RessourceNotFound(Exception):
    def __init__(self, message="Ressource not found"):
        Exception.__init__(self, message)
