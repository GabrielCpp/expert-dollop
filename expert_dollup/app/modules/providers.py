
from injector import Binder, singleton
from expert_dollup.infra.providers import WordProvider


def bind_providers(binder: Binder) -> None:
    with open("./assets/corncob_lowercase.txt") as f:
        words = [word for word in f.readlines() if word != '']

    binder.bind(WordProvider, to=lambda: WordProvider(words), scope=singleton)
