import pytest
from pet_boarding import boarding_fee, admission_ok, checkout_status


# ================= boarding_fee =================
# if pet_type not in INCLUDED_DAYS  -> True / False
def test_unknown_pet_type():
    with pytest.raises(ValueError):
        boarding_fee("hamster", 3, False)

# if days < 0  -> True / False
def test_negative_days():
    with pytest.raises(ValueError):
        boarding_fee("cat", -1, False)

def test_zero_days_is_valid():
    assert boarding_fee("cat", 0, False) == 0

# if is_premium and pet_type != "rabbit"
def test_premium_dog_gets_extra_included_day():
    # True and True -> included 3, extra 2, rate 30
    assert boarding_fee("dog", 5, True) == 60

def test_premium_rabbit_gets_no_extra_day():
    # True and False -> included stays 4, extra 2, rate 20
    assert boarding_fee("rabbit", 6, True) == 40

def test_non_premium_cat():
    # is_premium False -> included 3, extra 2, rate 20
    assert boarding_fee("cat", 5, False) == 40

# if extra <= 0  -> True / False (with boundary)
def test_within_included_days():
    assert boarding_fee("dog", 1, False) == 0

def test_exactly_included_days():
    # extra == 0 boundary
    assert boarding_fee("dog", 2, False) == 0

def test_one_day_over_included():
    # extra == 1
    assert boarding_fee("dog", 3, False) == 30

# if pet_type == "dog" -> rate 30 / else rate 20  (covered above)

# if extra > 10  -> True / False (with boundary)
def test_extra_exactly_ten_no_surcharge():
    # dog: extra 10, not > 10, rate 30
    assert boarding_fee("dog", 12, False) == 300

def test_dog_long_stay_surcharge():
    # extra 18 > 10, nested dog True: rate 30 + 10 + 5 = 45
    assert boarding_fee("dog", 20, False) == 810

def test_cat_long_stay_surcharge():
    # extra 17 > 10, nested dog False: rate 20 + 10 = 30
    assert boarding_fee("cat", 20, False) == 510


# ================= admission_ok =================
# if is_senior -> True (both outcomes of vaccinations >= 3)
def test_senior_enough_vaccinations():
    assert admission_ok(10, 3, True) is True

def test_senior_not_enough_vaccinations():
    assert admission_ok(10, 2, True) is False

# if pet_age_years < 1 -> True / False
def test_too_young():
    assert admission_ok(0.5, 3, False) is False

def test_exactly_one_year_old():
    assert admission_ok(1, 2, False) is True

# vaccinations >= 2 -> True / False
def test_admission_ok():
    assert admission_ok(4, 2, False) is True

def test_adult_not_enough_vaccinations():
    assert admission_ok(4, 1, False) is False


# ================= checkout_status =================
# is_long_stay False, is_weekend False -> cutoff 15
def test_regular_open():
    assert checkout_status(15, False, False) == "open"

def test_regular_late():
    assert checkout_status(14, False, False) == "late"

def test_regular_late_lower_edge():
    assert checkout_status(0, False, False) == "late"

def test_regular_closed():
    assert checkout_status(-1, False, False) == "closed"

# is_long_stay True, is_weekend True -> cutoff 50
def test_long_weekend_open():
    assert checkout_status(50, True, True) == "open"

def test_long_weekend_late():
    assert checkout_status(35, True, True) == "late"

def test_long_weekend_closed():
    assert checkout_status(34, True, True) == "closed"

# is_long_stay True, is_weekend False -> cutoff 30
def test_long_weekday_open():
    assert checkout_status(30, True, False) == "open"

# is_long_stay False, is_weekend True -> cutoff 35
def test_short_weekend_late():
    assert checkout_status(20, False, True) == "late"