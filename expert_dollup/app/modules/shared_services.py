from injector import Binder, inject
from expert_dollup.shared.handlers import RequestHandler


def bind_shared_services(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
