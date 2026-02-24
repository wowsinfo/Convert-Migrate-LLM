from typing import Iterator
from . import Backend
import re


class PythonBackend(Backend):
    def __init__(self, target_lang: str):
        self.target_lang = target_lang

    def break_down(self, code: str) -> Iterator[str]:
        top_level_regex = re.compile(r"(?=^def )", re.MULTILINE)
        for part in top_level_regex.split(code):
            part = part.strip()
            if part:
                yield part

    def build_rules(self) -> str:
        return self.default_rules(self.target_lang, "Python")
