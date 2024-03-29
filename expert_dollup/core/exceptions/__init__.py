from .ressource_not_found import RessourceNotFound
from .invalid_object import InvalidObject
from .validation_error import ValidationError
from .factory_seed_missing import FactorySeedMissing
from .invalid_usage_error import InvalidUsageError


from expert_dollup.shared.starlette_injection import DetailedError


class ReportGenerationError(DetailedError):
    pass


class AstEvaluationError(DetailedError):
    pass
