# pricing.py
# fee calculations, one function per mall
Gateway_Flat_Rate = 15.00
def calculate_hours(minutes):
    hours = minutes // 60
    # round up to the next hour, even when the time is  only a few minutes over the last hour
    if minutes % 60 != 0:
        hours = hours + 1
    if hours == 0:
        hours = 1
    return hours


def calculate_gateway_fee(minutes):
    return Gateway_Flat_Rate


def calculate_pavilion_fee(minutes):
    hours = calculate_hours(minutes)
    return hours * 10.00


def calculate_lalucia_fee(minutes):
    hours = calculate_hours(minutes)
    fee = hours * 12.00
    if fee > 60.00:
        fee = 60.00
    return fee


def calculate_fee(pricing_type, minutes):
    # to add another  mall just add another elif here
    if pricing_type == "flat":
        return calculate_gateway_fee(minutes)
    elif pricing_type == "hourly":
        return calculate_pavilion_fee(minutes)
    elif pricing_type == "hourly_capped":
        return calculate_lalucia_fee(minutes)
    # (no else - all 3 malls are covered above)
