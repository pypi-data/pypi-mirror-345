import pytest
import yaml


@pytest.fixture
def temp_config_dir(tmp_path):
    config_dir = tmp_path / "meshadmin"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_context(temp_config_dir):
    contexts = {
        "test-context": {
            "endpoint": "http://localhost:8000",
            "interface": "nebula1",
            "active": True,
        }
    }
    contexts_file = temp_config_dir / "contexts.yaml"
    with open(contexts_file, "w") as f:
        yaml.dump(contexts, f)
    return contexts
