"""
Test script to verify section exclusion logic in the orchestrator.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from orchestrator import _detect_exclusions

# --- Test the detection function ---
test_cases = [
    # (query, expected_excluded_set)
    ("Explain the Fourier Transform", set()),
    ("Explain gravity but do not give any math explanation", {"math"}),
    ("Explain gravity, don't give any visualisation", {"visual"}),
    ("Explain quantum mechanics, skip the explanation", {"explanation"}),
    ("Explain calculus, no math, no visual", {"math", "visual"}),
    ("Explain Newton's laws without math and without visualization", {"math", "visual"}),
    ("Explain relativity, remove the math derivation", {"math"}),
    ("What is photosynthesis? exclude the visual aid", {"visual"}),
    ("Explain thermodynamics, omit the math", {"math"}),
    ("Explain DNA, hide the diagram", {"visual"}),
    ("Don't give the conceptual explanation for black holes", {"explanation"}),
    ("Explain AI, leave out the equations", {"math"}),
    ("Explain fractions", set()),  # no exclusion
    ("Give me a mathematical proof of Euler's identity", set()),  # mentions math but no exclusion
]

print("=" * 60)
print("  Exclusion Detection Tests")
print("=" * 60)

passed = 0
failed = 0

for query, expected in test_cases:
    result = _detect_exclusions(query)
    status = "[PASS]" if result == expected else "[FAIL]"
    if result != expected:
        failed += 1
        print(f"  {status}  Query: {query!r}")
        print(f"         Expected: {expected}")
        print(f"         Got:      {result}")
    else:
        passed += 1
        print(f"  {status}  {query!r}  -> excluded: {result or '{none}'}")

print(f"\nResults: {passed} passed, {failed} failed out of {len(test_cases)} tests")
