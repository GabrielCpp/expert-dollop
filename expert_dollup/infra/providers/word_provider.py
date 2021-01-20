from typing import List
from secrets import choice


class WordProvider:
    def __init__(self, words: List[str]):
        self.words = words

    def pick(self, n: int = 1) -> List[str]:
        return [choice(self.words) for _ in range(0, n)]

    def pick_joined(self, n: int = 1, join_str: str = "_"):
        return join_str.join(self.pick(n))
