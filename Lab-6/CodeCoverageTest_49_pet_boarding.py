import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


# ---------- boarding_fee ----------
def test_unknown_pet_type():
    with pytest.raises(ValueError):
        boarding_fee("hamster", 3, False)

def test_negative_days():
    with pytest.raises(ValueError):
        boarding_fee("cat", -1, False)

def test_within_included_days():
    assert boarding_fee("dog", 1, False) == 0

def test_premium_dog_extra_days():
    # dog: 2 included + 1 premium = 3, extra = 2, rate 30
    assert boarding_fee("dog", 5, True) == 60

def test_cat_extra_days():
    # cat: 3 included, extra = 2, rate 20
    assert boarding_fee("cat", 5, False) == 40

def test_dog_long_stay_surcharge():
    # dog: extra = 18 (>10), rate 30 + 10 + 5 = 45
    assert boarding_fee("dog", 20, False) == 810


# ---------- admission_ok ----------
def test_admission_ok():
    assert admission_ok(4, 2, False) is True

def test_senior_pet():
    assert admission_ok(10, 3, True) is True

def test_too_young():
    assert admission_ok(0.5, 3, False) is False


# ---------- checkout_status ----------
def test_checkout_open_regular():
    # cutoff 15
    assert checkout_status(20, False, False) == "open"

def test_checkout_late_long_weekend():
    # cutoff 30 + 20 = 50, late window 35..49
    assert checkout_status(40, True, True) == "late"

def test_checkout_closed():
    assert checkout_status(-1, False, False) == "closed"