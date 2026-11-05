INCLUDED_DAYS = {"cat": 3, "dog": 2, "rabbit": 4}


def boarding_fee(pet_type, days, is_premium):
    if pet_type not in INCLUDED_DAYS:
        raise ValueError("unknown pet type")
    if days < 0:
        raise ValueError("invalid days")
    included = INCLUDED_DAYS[pet_type]
    if is_premium and pet_type != "rabbit":
        included += 1
    extra = days - included
    if extra <= 0:
        return 0
    if pet_type == "dog":
        rate = 30
    else:
        rate = 20
    if extra > 10:
        rate = rate + 10
        if pet_type == "dog":
            rate += 5
    return extra * rate


def admission_ok(pet_age_years, vaccinations, is_senior):
    if is_senior:
        return vaccinations >= 3
    if pet_age_years < 1:
        return False
    return vaccinations >= 2


def checkout_status(minutes_left, is_long_stay, is_weekend):
    if is_long_stay:
        cutoff = 30
    else:
        cutoff = 15
    if is_weekend:
        cutoff += 20
    if minutes_left >= cutoff:
        return "open"
    elif minutes_left >= cutoff - 15:
        return "late"
    return "closed"
