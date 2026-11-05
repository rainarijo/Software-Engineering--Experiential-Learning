import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status

# Example test cases:
def test_within_included_days():
    assert boarding_fee("dog", 1, False) == 0

def test_admission_ok():
    assert admission_ok(4, 2, False) is True

# Write the rest of the test cases so that the code is 90-100% covered.
