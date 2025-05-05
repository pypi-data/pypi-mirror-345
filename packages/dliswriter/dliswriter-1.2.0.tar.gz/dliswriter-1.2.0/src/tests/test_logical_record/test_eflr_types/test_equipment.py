import pytest
from typing import Any

from dliswriter.logical_record.eflr_types import EquipmentSet, EquipmentItem
from dliswriter import AttrSetup, high_compatibility_mode_decorator


@pytest.mark.parametrize(("name", "status", "serial_number"), (
        ("EQ1", 1, "9101-21391"),
        ("EQ2", 0, "5559101-21391"),
        ("EqX", 1, "12311")
))
def test_creation(name: str, status: int, serial_number: str) -> None:
    """Check that EquipmentObject instances are correctly created from config."""

    eq = EquipmentItem(
        name,
        status=status,
        serial_number=serial_number,
        parent=EquipmentSet()
    )

    assert eq.name == name
    assert eq.status.value == status
    assert isinstance(eq.status.value, int)
    assert eq.serial_number.value == serial_number
    assert isinstance(eq.serial_number.value, str)

    assert isinstance(eq.parent, EquipmentSet)
    assert eq.parent.set_name is None


def test_params_and_units() -> None:
    """Check setting up EquipmentObject's parameters and units."""

    eq = EquipmentItem(
        "Equipment-1",
        **{
            'height': {'value': 140, 'units': 'in'},
            'length': AttrSetup(230.78, 'cm'),
            'minimum_diameter': AttrSetup(2.3, units='m'),
            'maximum_diameter': AttrSetup(value=3.2, units='m'),
            'weight': {'value': 1.2, 'units': 't'},
            'hole_size': {'value': 323.2, 'units': 'm'},
            'pressure': {'value': 18000, 'units': 'psi'},
            'temperature': {'value': 24, 'units': 'degC'},
            'vertical_depth': {'value': 587, 'units': 'm'},
            'radial_drift': AttrSetup(23.22, 'm'),
            'angular_drift': AttrSetup(32.5, 'm')
        },
        parent=EquipmentSet()
    )

    def check(name: str, val: Any, unit: str) -> None:
        attr = getattr(eq, name)
        assert attr.value == val
        assert attr.units == unit

    check('height', 140, 'in')
    check('length', 230.78, 'cm')
    check('minimum_diameter', 2.3, 'm')
    check('maximum_diameter', 3.2, 'm')
    check('weight', 1.2, 't')
    check('hole_size', 323.2, 'm')
    check('pressure', 18000, 'psi')
    check('temperature', 24, 'degC')
    check('vertical_depth', 587, 'm')
    check('radial_drift', 23.22, 'm')
    check('angular_drift', 32.5, 'm')


@pytest.mark.parametrize("sn", ("124-111", "123_B3", "A12"))
@high_compatibility_mode_decorator
def test_serial_number_compatible(sn: str) -> None:
    EquipmentItem("EQUIPMENT-1", serial_number=sn, parent=EquipmentSet())


@pytest.mark.parametrize("sn", ("123.1", "112 131", "213/1"))
@high_compatibility_mode_decorator
def test_type_not_compatible(sn: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        EquipmentItem("EQUIPMENT-1", serial_number=sn, parent=EquipmentSet())


@pytest.mark.parametrize("name", ("EQ-1", "EQP3", "11C"))
@high_compatibility_mode_decorator
def test_name_compatible(name: str) -> None:
    EquipmentItem(name, parent=EquipmentSet())


@pytest.mark.parametrize("name", ("EQ 1", "Equip-1", "EQ.32"))
@high_compatibility_mode_decorator
def test_label_not_compatible(name: str) -> None:
    with pytest.raises(ValueError, match=".*strings can contain only uppercase characters, digits, dashes, .*"):
        EquipmentItem(name, parent=EquipmentSet())
