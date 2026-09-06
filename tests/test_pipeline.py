import datetime as dt
import pandas as pd
from validate_submission import REQUIRED_COLUMNS, validate

def test_predictions_schema(tmp_path):
    # Tests that the output structure satisfies validation rules
    sample_file = tmp_path / "dummy_preds.csv"
    data = {col: [] for col in REQUIRED_COLUMNS}
    pd.DataFrame(data).to_csv(sample_file, index=False)
    
    # Run validator logic
    problems = validate(sample_file)
    # File is empty of rows, so it should catch row count issues without crashing
    assert any("expected 120 rows" in p for p in problems)