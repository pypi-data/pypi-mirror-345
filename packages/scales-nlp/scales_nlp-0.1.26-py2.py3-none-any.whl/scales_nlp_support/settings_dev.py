from pathlib import Path

# Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXCLUDE_CASES = PROJECT_ROOT / 'data' / 'recap_evaluation' / 'dump_2016_ucids.csv'
RECAP_DUMP = PROJECT_ROOT / 'data' / 'recap_evaluation'/ 'dump_2016.csv'
