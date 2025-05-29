from glob import glob
from tqdm import tqdm
from pathlib import Path
import subprocess
import pandas as pd
import json


def safe_run_souffle(program):
  try:
    output = subprocess.run(["souffle", program],
                            check=True,
                            capture_output=True,
                            text=True)
    return output.returncode == 0
  except Exception as _e:
    return False


def safe_read_csv(path):
  try:
    return pd.read_csv(path, header=None)
  except pd.errors.EmptyDataError:
    # Return an empty DataFrame if the file has no data
    return pd.DataFrame()


def main():
  violations, compliances, errors = [], [], []
  programs = glob("experiments/phi4/programs/*.dl")

  for program in tqdm(programs):
    violation_file = Path("violation.csv")
    violation_file.unlink(missing_ok=True)
    output = safe_run_souffle(program)
    if output and violation_file.exists():
      df = safe_read_csv(violation_file)
      if len(df) > 0:
        violations.append(program)
      else:
        compliances.append(program)
    else:
      errors.append(program)

  ## remove generated csv files
  violation_file = Path("violation.csv")
  violation_file.unlink(missing_ok=True)

  stats = {
      "overall": {
          "violations": len(violations),
          "compliances": len(compliances),
          "errors": len(errors)
      },
      "details": {
          "violations": violations,
          "compliances": compliances,
          "errors": errors
      }
  }
  json.dump(stats, open("experiments/phi4/stats.json", "w"), indent=2)


if __name__ == "__main__":
  main()
