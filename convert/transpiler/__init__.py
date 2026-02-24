from ..backend import Backend
from ..engine import Engine
from ..post_processing import PostProcessing
from time import sleep

_MAX_RETRIES = 3
_RETRY_PROMPT = (
    "\n###\nYour previous response did not contain a fenced code block. "
    "Output ONLY the translated code inside a single fenced code block (```)."
)


class Transpiler:
    """
    Convert the code from one language to another,
    breaking down the code into smaller parts,
    use the engine to convert the code,
    and finally merge the code back together.
    """

    def __init__(
        self,
        engine: Engine,
        backend: Backend,
        custom_rules: str = None,
        post_processing: list[PostProcessing] = None,
    ):
        self.engine = engine
        self.backend = backend
        self.custom_rules = custom_rules
        self.post_processing = list(post_processing) if post_processing else []

    def switch_engine(self, engine: Engine):
        self.engine = engine

    def switch_backend(self, backend: Backend):
        self.backend = backend

    def add_post_processing(self, post_processing: PostProcessing):
        self.post_processing.append(post_processing)

    def remove_post_processing(self, post_processing: PostProcessing):
        self.post_processing.remove(post_processing)

    def update_custom_rules(self, custom_rules: str):
        self.custom_rules = custom_rules

    # region Transpile

    def _translate_part(self, prompt: str, system_prompt: str) -> str:
        """
        Send a prompt to the engine and parse the code block.
        Retries with corrective feedback up to _MAX_RETRIES times on parse failure.
        """
        current_prompt = prompt
        for attempt in range(_MAX_RETRIES):
            response = self.engine.get_chat_response(current_prompt, system_prompt)
            sleep(0.2)
            try:
                return self.backend.parse_codeblock(response)
            except ValueError:
                if attempt < _MAX_RETRIES - 1:
                    current_prompt = prompt + _RETRY_PROMPT
                else:
                    raise

    def convert_code(self, code: str) -> str:
        """
        Convert the code from one language to another
        """
        rules = self.backend.build_rules()
        if self.custom_rules:
            rules += self.custom_rules

        system_prompt = self.backend.build_system_prompt()
        transpile_parts = []
        for part in self.backend.break_down(code):
            prompt = part + rules
            try:
                transpile_parts.append(self._translate_part(prompt, system_prompt))
            except ValueError:
                transpile_parts.append("===>>> review manually\n" + part + "\n<<<===\n")

        before_processing = self.backend.merge_code(transpile_parts)
        after_processing = before_processing
        for process in self.post_processing:
            after_processing = process.process(before_processing)
        return after_processing

    def convert_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
        return self.convert_code(code)

    # endregion
