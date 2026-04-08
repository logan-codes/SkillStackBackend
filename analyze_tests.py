import pandas as pd

df = pd.read_csv("test_results.csv")
print("=== TEST RESULTS SUMMARY ===")
print(f"Total: {len(df)} tests")
print(f"Pass: {len(df[df.Result == 'PASS'])}")
print(f"Fail: {len(df[df.Result == 'FAIL'])}")
print()
print("=== FAILED TESTS ===")
for _, row in df[df.Result == "FAIL"].iterrows():
    print(
        f"{row.Test_ID}: {row.Test_Case} - Expected: {row.Expected_Status}, Got: {row.Actual_Status}"
    )
