from injector import Binder, singleton
from expert_dollup.infra.providers import WordProvider
from expert_dollup.shared.starlette_injection import Clock, DateTimeClock


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != ""]

    binder.bind(WordProvider, to=lambda: WordProvider(words), scope=singleton)
    binder.bind(Clock, to=DateTimeClock(), scope=singleton)
