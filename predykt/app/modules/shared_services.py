from injector import Binder, inject
from predykt.shared.handlers import RequestHandler


def bind_shared_services(binder: Binder) -> None:
    binder.bind(RequestHandler, inject(RequestHandler))
