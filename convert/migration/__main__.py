from ..transpiler import Transpiler
from ..backend.flutter import FlutterBackend
from ..backend.react_native import ReactNativeBackend
from ..engine import Engine, EngineConfig
from ..post_processing.remove_keyword import RemoveImport
from convert.key import API_KEY
from . import ProjectMigration

# engine = Engine.create_lm_studio_engine(
#     "codellama-7b.q4_0", config=EngineConfig()
# )
engine = Engine.create_chatgpt_engine(
    API_KEY,
    "gpt-4o",
    EngineConfig(max_tokens=None),
)
backend = ReactNativeBackend("Flutter", tab_size=2)
transpiler = Transpiler(
    engine,
    backend,
    "",
    [RemoveImport()],
)

migration = ProjectMigration(
    r"legacy\reactnative\src", 
    (".ts", ".tsx", ".js", ".jsx"), 
    ".dart", 
    "flutter"
)

migration.migrate(transpiler)
