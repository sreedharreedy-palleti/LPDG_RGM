import pathlib
import pandas as pd
from validate_submission import REQUIRED_COLUMNS, validate, normalise_gateway_id

def test_gateway_id_normalisation():
    assert normalise_gateway_id("001122334455") == "001122334455"
    assert normalise_gateway_id("00:11:22:33:44:55") == "001122334455"
    assert normalise_gateway_id("invalid-mac") is None

def test_validate_detects_empty_csv(tmp_path: pathlib.Path):
    dummy_csv = tmp_path / "test_empty.csv"
    pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(dummy_csv, index=False)
    problems = validate(dummy_csv)
    assert any("expected 120 rows" in p for p in problems)