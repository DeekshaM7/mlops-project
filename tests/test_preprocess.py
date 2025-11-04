import os


def test_preprocess_script_smoke():
    assert os.path.exists("configs/params.yaml")
    # Smoke test: ensure module is importable
    __import__("src.data.preprocess")
