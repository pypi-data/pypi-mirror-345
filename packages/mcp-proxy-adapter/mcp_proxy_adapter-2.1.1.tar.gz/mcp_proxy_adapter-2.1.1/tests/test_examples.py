import subprocess
import sys
import os
import pytest

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "examples")

@pytest.mark.parametrize("script,expected", [
    ("help_usage.py", ["Project help", "Adapter help"]),
    ("help_best_practices.py", ["Project help", "Adapter help"]),
    ("docstring_and_schema_example.py", ["Tool description from docstring", "sum of two numbers"]),
    ("testing_example.py", ["All tests passed"]),
    ("extension_example.py", ["Ping", "Help (all)", "Help (ping)", "Help (notfound)"]),
])
def test_example_scripts(script, expected):
    """Test that example script runs and produces expected output."""
    script_path = os.path.join(EXAMPLES_DIR, script)
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    assert result.returncode == 0, f"{script} failed: {result.stderr}"
    for key in expected:
        assert key in result.stdout, f"{script} output missing: {key}"

# FastAPI app smoke-test (project_structure_example.py)
def test_project_structure_example_import():
    """Test that project_structure_example.py can be imported and app initialized."""
    import importlib.util
    script_path = os.path.join(EXAMPLES_DIR, "project_structure_example.py")
    spec = importlib.util.spec_from_file_location("project_structure_example", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert hasattr(module, "app"), "FastAPI app not found in project_structure_example.py"
    assert hasattr(module, "adapter"), "Adapter not found in project_structure_example.py" 