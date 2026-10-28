"""Tests written to reach high LINE (code) coverage of laundry_service.py.

Run with:
    coverage run -m pytest CodeCoverageTest_laundry_service.py
    coverage report -m
"""
import pytest
from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# ---------------------------------------------------------------------------
# extra_weight_charge
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
# order_acceptable
# ---------------------------------------------------------------------------
def test_order_acceptable():
    assert order_acceptable(10, 20, False) is True


def test_delicate_order_within_item_limit():
    assert order_acceptable(3, 4, True) is True


def test_overweight_order_rejected():
    assert order_acceptable(30, 10, False) is False


# ---------------------------------------------------------------------------
# dropoff_status
# ---------------------------------------------------------------------------
def test_dropoff_accepted():
    assert dropoff_status(100, False, False) == "accepted"


def test_dropoff_late():
    # cutoff 60, late window is 40-59 minutes
    assert dropoff_status(45, False, False) == "late"


def test_dropoff_rejected():
    assert dropoff_status(10, False, False) == "rejected"


def test_dropoff_bedding_has_longer_cutoff():
    # cutoff 90 for bedding, so 100 minutes is accepted
    assert dropoff_status(100, True, False) == "accepted"


def test_dropoff_express_has_longer_cutoff():
    # cutoff 60 + 30 = 90, so 80 minutes falls in the late window (70-89)
    assert dropoff_status(80, False, True) == "late"
