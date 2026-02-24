from abc import ABC, abstractmethod
from typing import Iterator


class Backend(ABC):
    """
    Backend for any programming language:
    - Instruct how to break down the code into smaller parts
    """

    @abstractmethod
    def break_down(self, code: str) -> Iterator[str]:
        """
        Break down the code into smaller parts
        """
        pass

    @abstractmethod
    def build_rules(self) -> str:
        """
        Build the rules/instructions for the engine
        """
        pass

    # region generic methods

    def merge_code(self, parts: list[str]) -> str:
        """
        Merge the parts back together
        """
        return "\n\n".join(parts)

    def build_system_prompt(self) -> str:
        """
        Returns a system-level role prompt for the engine.
        Subclasses may override to provide language-specific context.
        """
        return (
            "You are an expert code translator. "
            "Convert code exactly as instructed. "
            "Output ONLY a single fenced code block with no explanations or surrounding text."
        )

    def default_rules(self, target_lang: str, original: str) -> str:
        """
        Default rules for the engine, free to update as needed
        """
        return (
            f"\n###\nTranslate the code above from `{original}` to `{target_lang}`. "
            f"Replace all libraries, frameworks, and APIs with direct `{target_lang}` equivalents. "
            f"Output the complete, fully-functional `{target_lang}` code in a single fenced code block. "
            f"Every function, method, and class must be fully implemented — no placeholders."
        )


    def parse_codeblock(self, text: str) -> str:
        """
        Parse the codeblock from the response
        """
        start_pos = text.find("```")
        if start_pos == -1:
            raise ValueError("Codeblock not found")
        start = start_pos + 3
        end = text.find("```", start)
        if end == -1:
            raise ValueError("Codeblock not found")
        result = text[start:end].strip()
        # skip the language identifier line if present (e.g. "python", "dart")
        lines = result.split("\n")
        if lines and lines[0].strip().replace("-", "").replace("_", "").isalnum():
            return "\n".join(lines[1:])
        return result

    # endregion
