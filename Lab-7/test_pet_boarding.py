from hypothesis import given, settings, strategies as st
from pet_boarding import parse_booking, stay_average, payable_fee


# ---------- 1. Completely random input: any text or None ----------

@given(st.text() | st.none())
def test_parse_booking_no_crash(s):
    try:
        parse_booking(s)
    except Exception as e:
        assert False, f"parse_booking crashed with: {e!r}"


@given(st.text() | st.none())
def test_stay_average_no_crash(s):
    try:
        stay_average(s)
    except Exception as e:
        assert False, f"stay_average crashed with: {e!r}"


@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r}"


# ---------- 2. Input that LOOKS valid (uses the right separators) ----------
# These reach deeper into each function than random text does.

@settings(max_examples=300)
@given(st.text(alphabet="dogcat:0123456789.-e ", max_size=12))
def test_parse_booking_near_valid_no_crash(s):
    try:
        parse_booking(s)
    except Exception as e:
        assert False, f"parse_booking crashed with: {e!r}"


@settings(max_examples=300)
@given(st.text(alphabet="0123456789,.- ", max_size=12))
def test_stay_average_near_valid_no_crash(s):
    try:
        stay_average(s)
    except Exception as e:
        assert False, f"stay_average crashed with: {e!r}"


@settings(max_examples=300)
@given(st.text(alphabet="0123456789|.-naif ", max_size=12))
def test_payable_fee_near_valid_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r}"


# ---------- 3. Properties on valid input ----------

@given(st.lists(st.integers(min_value=0, max_value=365), min_size=1, max_size=20))
def test_stay_average_within_range(days):
    result = stay_average(",".join(str(d) for d in days))
    assert min(days) <= result <= max(days)


@given(st.floats(min_value=0, max_value=1e6), st.floats(min_value=0, max_value=1e6))
def test_payable_fee_never_negative(fee, discount):
    result = payable_fee(f"{fee}|{discount}")
    assert result is not None and result >= 0