"""Tests written to reach high BRANCH coverage of laundry_service.py.

This file contains the line-coverage tests plus tests for the branch the
earlier suite never took (a heavy order at standard speed) and for the
boundary values of every comparison.

Run with:
    coverage run --branch -m pytest BranchCoverageTest_laundry_service.py
    coverage report -m
"""
import pytest
from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# ---------------------------------------------------------------------------
# extra_weight_charge: line-coverage tests
# ---------------------------------------------------------------------------
def test_within_included_weight():
    assert extra_weight_charge("regular", 4, "standard", False) == 0


def test_unknown_garment_type_raises():
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("curtains", 4, "standard", False)


def test_negative_weight_raises():
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_member_gets_two_extra_kg_included():
    # member on "regular": included 5 + 2 = 7, so 8 kg leaves 1 kg extra
    assert extra_weight_charge("regular", 8, "standard", True) == 30


def test_standard_speed_extra_charge():
    # 10 kg - 5 kg included = 5 kg extra at 30 per kg
    assert extra_weight_charge("regular", 10, "standard", False) == 150


def test_express_speed_extra_charge():
    # 5 kg extra at 50 per kg
    assert extra_weight_charge("regular", 10, "express", False) == 250


def test_heavy_express_surcharge():
    # 15 kg extra: rate 50 + 15 (heavy) + 10 (express heavy) = 75
    assert extra_weight_charge("regular", 20, "express", False) == 1125


# ---------------------------------------------------------------------------
# extra_weight_charge: branch and boundary tests
# ---------------------------------------------------------------------------
def test_heavy_standard_surcharge_without_express_bonus():
    # BRANCH: extra > 10 is True but speed == "express" is False.
    # 15 kg extra: rate 30 + 15 (heavy) = 45
    assert extra_weight_charge("regular", 20, "standard", False) == 675


def test_zero_weight_is_free():
    assert extra_weight_charge("regular", 0, "standard", False) == 0


def test_exactly_included_weight_is_free():
    # extra == 0 hits the "extra <= 0" boundary
    assert extra_weight_charge("regular", 5, "standard", False) == 0


def test_one_kg_over_included_is_charged():
    assert extra_weight_charge("regular", 6, "standard", False) == 30


def test_extra_of_exactly_ten_has_no_heavy_surcharge():
    # extra == 10 is NOT > 10, so the plain rate applies
    assert extra_weight_charge("regular", 15, "standard", False) == 300


def test_extra_of_eleven_gets_heavy_surcharge():
    # extra == 11 is > 10: rate 30 + 15 = 45
    assert extra_weight_charge("regular", 16, "standard", False) == 495


def test_member_allowance_does_not_apply_to_bedding():
    # bedding included stays 8 even for members, so 9 kg leaves 1 kg extra
    assert extra_weight_charge("bedding", 9, "standard", True) == 30


def test_member_allowance_applies_to_delicate():
    # delicate included 3 + 2 = 5, so 6 kg leaves 1 kg extra
    assert extra_weight_charge("delicate", 6, "standard", True) == 30


def test_non_member_delicate_charge():
    # delicate included 3, so 6 kg leaves 3 kg extra at 30
    assert extra_weight_charge("delicate", 6, "standard", False) == 90


def test_non_member_bedding_within_allowance():
    assert extra_weight_charge("bedding", 8, "standard", False) == 0


def test_unrecognised_speed_is_charged_at_express_rate():
    # Documents current behaviour: any speed other than "standard"
    # falls through to the 50 rate.
    assert extra_weight_charge("regular", 10, "overnight", False) == 250


# ---------------------------------------------------------------------------
# order_acceptable
# ---------------------------------------------------------------------------
def test_order_acceptable():
    assert order_acceptable(10, 20, False) is True


def test_delicate_order_within_item_limit():
    assert order_acceptable(3, 4, True) is True


def test_overweight_order_rejected():
    assert order_acceptable(30, 10, False) is False


@pytest.mark.parametrize(
    "weight, items, is_delicate, expected",
    [
        (3, 5, True, True),       # delicate limit is exactly 5 items
        (3, 6, True, False),      # one item over the delicate limit
        (100, 5, True, True),     # delicate orders ignore the weight limit
        (25, 40, False, True),    # exactly at both normal limits
        (26, 1, False, False),    # one kg over the weight limit
        (10, 41, False, False),   # one item over the item limit
    ],
)
def test_order_acceptable_boundaries(weight, items, is_delicate, expected):
    assert order_acceptable(weight, items, is_delicate) is expected


# ---------------------------------------------------------------------------
# dropoff_status
# ---------------------------------------------------------------------------
def test_dropoff_accepted():
    assert dropoff_status(100, False, False) == "accepted"


def test_dropoff_late():
    assert dropoff_status(45, False, False) == "late"


def test_dropoff_rejected():
    assert dropoff_status(10, False, False) == "rejected"


def test_dropoff_bedding_has_longer_cutoff():
    assert dropoff_status(100, True, False) == "accepted"


def test_dropoff_express_has_longer_cutoff():
    assert dropoff_status(80, False, True) == "late"


@pytest.mark.parametrize(
    "minutes, has_bedding, is_express, expected",
    [
        # plain: cutoff 60, late window 40-59
        (60, False, False, "accepted"),
        (59, False, False, "late"),
        (40, False, False, "late"),
        (39, False, False, "rejected"),
        # bedding: cutoff 90, late window 70-89
        (90, True, False, "accepted"),
        (89, True, False, "late"),
        (70, True, False, "late"),
        (69, True, False, "rejected"),
        # express: cutoff 90, late window 70-89
        (90, False, True, "accepted"),
        (70, False, True, "late"),
        (69, False, True, "rejected"),
        # bedding and express: cutoff 120, late window 100-119
        (120, True, True, "accepted"),
        (100, True, True, "late"),
        (99, True, True, "rejected"),
        # nothing left before closing
        (0, False, False, "rejected"),
    ],
)
def test_dropoff_status_boundaries(minutes, has_bedding, is_express, expected):
    assert dropoff_status(minutes, has_bedding, is_express) == expected
