"""
Tests for Backend and Transpiler logic using a stubbed engine.
Verifies break_down, parse_codeblock, build_rules, and convert_code
without making any real LLM calls.
"""

import unittest
from convert.backend.console import ConsoleBackend
from convert.backend.cpp import CppBackend
from convert.backend.flutter import FlutterBackend
from convert.backend.python import PythonBackend
from convert.backend.react_native import ReactNativeBackend
from convert.transpiler import Transpiler

# --- Shared quicksort snippet (JS) used across backend tests ---
QUICKSORT_JS = """function quicksort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const mid = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  return [...quicksort(left), ...mid, ...quicksort(right)];
}"""


class StubEngine:
    """Returns a minimal valid code block so parse_codeblock always succeeds."""

    def __init__(self, lang: str = "dart"):
        self.lang = lang
        self.call_count = 0

    def get_chat_response(self, prompt: str, system_prompt: str = None) -> str:
        self.call_count += 1
        return f"```{self.lang}\n// translated\nvoid main() {{}}\n```"


class TestParseCodeblock(unittest.TestCase):
    def setUp(self):
        self.backend = ConsoleBackend("Dart")

    def test_with_language_identifier(self):
        result = self.backend.parse_codeblock("```dart\nvoid main() {}\n```")
        self.assertEqual(result, "void main() {}")

    def test_without_language_identifier(self):
        result = self.backend.parse_codeblock("```\nvoid main() {}\n```")
        self.assertEqual(result, "void main() {}")

    def test_missing_codeblock_raises(self):
        with self.assertRaises(ValueError):
            self.backend.parse_codeblock("no code block here")

    def test_unclosed_codeblock_raises(self):
        with self.assertRaises(ValueError):
            self.backend.parse_codeblock("```dart\nvoid main() {}")


class TestConsoleBackendBreakdown(unittest.TestCase):
    def test_yields_code_as_single_part(self):
        backend = ConsoleBackend("Dart")
        parts = list(backend.break_down(QUICKSORT_JS))
        self.assertEqual(len(parts), 1)
        self.assertIn("quicksort", parts[0])


class TestPythonBackendBreakdown(unittest.TestCase):
    PY_CODE = "import os\n\ndef foo():\n    pass\n\ndef bar():\n    return 1\n"

    def test_splits_functions_preserving_preamble(self):
        backend = PythonBackend("Julia")
        parts = list(backend.break_down(self.PY_CODE))
        self.assertEqual(len(parts), 3)
        self.assertIn("import os", parts[0])
        self.assertTrue(parts[1].startswith("def foo"))
        self.assertTrue(parts[2].startswith("def bar"))

    def test_no_empty_parts(self):
        backend = PythonBackend("Julia")
        for part in backend.break_down(self.PY_CODE):
            self.assertTrue(part.strip(), "Empty part yielded")


class TestFlutterBackendBreakdown(unittest.TestCase):
    DART_CODE = """\
class Foo {
  void bar() {
    print('hi');
  }
}

class Baz {
  int x = 1;
}"""

    def test_splits_on_top_level_braces(self):
        backend = FlutterBackend("Kotlin")
        parts = list(backend.break_down(self.DART_CODE))
        self.assertGreater(len(parts), 1)

    def test_no_empty_parts(self):
        backend = FlutterBackend("Kotlin")
        for part in backend.break_down(self.DART_CODE):
            self.assertTrue(part.strip(), "Empty part yielded")


class TestReactNativeBackendBreakdown(unittest.TestCase):
    TS_CODE = """\
const Foo = () => {
  return null;
};

const Bar = () => {
  return null;
};"""

    def test_splits_on_top_level_braces(self):
        backend = ReactNativeBackend("Flutter")
        parts = list(backend.break_down(self.TS_CODE))
        self.assertGreater(len(parts), 1)

    def test_no_empty_parts(self):
        backend = ReactNativeBackend("Flutter")
        for part in backend.break_down(self.TS_CODE):
            self.assertTrue(part.strip(), "Empty part yielded")


class TestCppBackendBreakdown(unittest.TestCase):
    CPP_CODE = """\
#include <vector>

void quicksort(std::vector<int>& arr, int low, int high) {
    if (low < high) {}
}

int main() {
    return 0;
}"""

    def test_splits_on_top_level_braces(self):
        backend = CppBackend("Rust")
        parts = list(backend.break_down(self.CPP_CODE))
        self.assertGreater(len(parts), 1)

    def test_no_empty_parts(self):
        backend = CppBackend("Rust")
        for part in backend.break_down(self.CPP_CODE):
            self.assertTrue(part.strip(), "Empty part yielded")

    def test_build_rules_mentions_rust(self):
        backend = CppBackend("Rust")
        self.assertIn("Rust", backend.build_rules())
        self.assertIn("C++", backend.build_rules())

    def test_system_prompt_mentions_rust(self):
        backend = CppBackend("Rust")
        self.assertIn("Rust", backend.build_system_prompt())


class TestTranspilerQuicksort(unittest.TestCase):
    """
    End-to-end transpiler test: quicksort in JS converted to Dart/C++/Rust
    using a stub engine that returns a minimal valid code block.
    """

    def _run(self, backend, lang: str):
        engine = StubEngine(lang)
        transpiler = Transpiler(engine, backend)
        result = transpiler.convert_code(QUICKSORT_JS)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertNotIn("===>>> review manually", result)
        return result

    def test_quicksort_js_to_dart(self):
        self._run(ConsoleBackend("Dart"), "dart")

    def test_quicksort_js_to_cpp(self):
        self._run(ConsoleBackend("C++"), "cpp")

    def test_quicksort_js_to_rust(self):
        self._run(ConsoleBackend("Rust"), "rust")

    def test_quicksort_via_cpp_backend_to_rust(self):
        self._run(CppBackend("Rust"), "rust")

    def test_retry_on_missing_codeblock(self):
        """Engine returns plain text first, then a valid codeblock — retry should recover."""

        class FlakeyEngine:
            def __init__(self):
                self.calls = 0

            def get_chat_response(self, prompt, system_prompt=None):
                self.calls += 1
                if self.calls == 1:
                    return "Here is the translation:\nvoid main() {}"
                return "```dart\nvoid main() {}\n```"

        engine = FlakeyEngine()
        transpiler = Transpiler(engine, ConsoleBackend("Dart"))
        result = transpiler.convert_code(QUICKSORT_JS)
        self.assertEqual(result, "void main() {}")
        self.assertEqual(engine.calls, 2)


if __name__ == "__main__":
    unittest.main()
