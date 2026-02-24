from typing import Iterator
from . import Backend
import re


class CppBackend(Backend):
    def __init__(self, target_lang: str):
        self.target_lang = target_lang

    def break_down(self, code: str) -> Iterator[str]:
        # Split at top-level closing braces (class/function boundaries)
        top_level_regex = re.compile(r"^}$|^};$", re.MULTILINE)
        for part in top_level_regex.split(code):
            part = part.strip()
            if part:
                yield part

    def build_rules(self) -> str:
        return self.default_rules(self.target_lang, "C++")

    def build_system_prompt(self) -> str:
        if self.target_lang.lower() == "rust":
            extra = (
                "Use ownership, lifetimes, and standard library types correctly. "
                "Prefer safe Rust — avoid `unsafe` unless required by the original logic."
            )
        else:
            extra = f"Produce idiomatic {self.target_lang} using its standard library and conventions."
        return (
            f"You are an expert C++ to {self.target_lang} translator. "
            f"Convert C++ code to {self.target_lang} exactly as instructed. "
            f"{extra} "
            "Output ONLY a single fenced code block with no explanations or surrounding text."
        )
