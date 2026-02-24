from . import Transpiler
from ..engine import Engine, EngineConfig
from ..backend.python import PythonBackend
from ..post_processing.remove_keyword import RemoveImport
from convert.key import API_KEY

# engine = Engine.create_lm_studio_engine("codegeex4-all-9b-q4_k_s")
# engine = Engine.create_lm_studio_engine("codellama-7b.q4_0")
# engine = Engine.create_lm_studio_engine("qwen2.5-coder-7b-instruct")
engine = Engine.create_chatgpt_engine(API_KEY, "gpt-4o", EngineConfig(max_tokens=None))
backend = PythonBackend("Julia")
transpiler = Transpiler(
    engine,
    backend,
    custom_rules="",
    # post_processing=[RemoveImport()],
)

output = transpiler.convert_file(r"..\automation\scripts\generate.py")
with open("temp\\generated.jl", "w", encoding="utf-8") as file:
    file.write(output)
