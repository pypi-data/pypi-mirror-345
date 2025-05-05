import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any, Union, Optional, Generator
import numpy as np

from dliswriter.utils.internal.struct_writer import write_struct_obname
from dliswriter.logical_record.core.attribute.attribute import Attribute
from dliswriter.utils.internal.value_checkers import validate_string
from dliswriter.utils import enums

if TYPE_CHECKING:
    from dliswriter.logical_record.core.eflr.eflr_set import EFLRSet
    from dliswriter.logical_record.core.attribute.subtypes import DimensionAttribute


logger = logging.getLogger(__name__)


class AttrSetup:
    """Convenience class to pass setup for an Attribute without creating a dictionary."""

    # Note: the initial plan was to make it a dataclass, but this doesn't give the PyCharm IDE typing hints,
    # which is one of the main points of this class

    def __init__(self, value: Optional[Any] = None, units: Optional[Union[str, enums.Unit]] = None) -> None:
        """Initialise AttrSetup with any of the passed values."""

        self.value = value
        self.units = units
        # Note: no checks done here, because they're done in EFLRItem/Attribute later anyway

    def items(self) -> Generator:
        for item_name in ('value', 'units'):
            if (item_value := getattr(self, item_name)) is not None:
                yield item_name, item_value


class EFLRItem:
    """Model an item belonging to an Explicitly Formatted Logical Record - e.g. a particular channel."""

    parent_eflr_class: type["EFLRSet"] = NotImplemented

    def __init__(self, name: str, parent: "EFLRSet", origin_reference: Optional[int] = None, **kwargs: Any) -> None:
        """Initialise an EFLRItem.

        Args:
            name                :   Name of the item. This will be the name it is stored with in the created DLIS file.
            parent              :   EFLRTable instance this item belongs to. If not provided,
                                        retrieved/made based on set_name.
            origin_reference    :   Common for EFLRItems sharing the same Origin.
            **kwargs            :   Values to be set in attributes of this item.

        Note:
            When a subclass of EFLRItem is defined, all the attributes should be defined before calling
            super().__init__. This makes it possible for values of attributes to be set here, through 'set_attributes'
            method call.

        """

        self.name = validate_string(name)    #: name of the item

        self._check_parent(parent)
        self._parent = parent  #: EFLRSet instance this item belongs to
        self._parent.register_item(self)

        #: origin reference value, common for records sharing origin
        self._origin_reference: Union[int, None] = self._validate_origin_reference(origin_reference, allow_none=True)

        #: copy number of the item - ith EFLRItem of the same name and type
        self._copy_number = self._compute_copy_number()

        for attribute in self.attributes.values():
            attribute.parent_eflr = self

        self.set_attributes(**{k: v for k, v in kwargs.items() if v is not None})

    @property
    def parent(self) -> "EFLRSet":
        """EFLRSet instance that this EFLRItem is a part of."""

        return self._parent

    @property
    def copy_number(self) -> int:
        """Copy number of this EFLRItem."""

        return self._copy_number

    @property
    def origin_reference(self) -> Union[int, None]:
        """Reference to the Origin associated with this EFLRItem."""

        return self._origin_reference

    @origin_reference.setter
    def origin_reference(self, v: int) -> None:
        """Set a new origin reference (point to a different Origin)."""

        self._origin_reference = self._validate_origin_reference(v)

    @staticmethod
    def _validate_origin_reference(v: Union[int, None], allow_none: bool = False) -> Union[int, None]:
        """Check that the provided origin reference value is an integer (or None, depending on the setup).

        Return the provided origin reference value (if it's correct). Raise an error otherwise.
        """

        if v is None and allow_none:
            return None

        if not isinstance(v, int):
            raise TypeError(f"Origin reference must be an integer; got {type(v)}: {v}")

        return v

    def _compute_copy_number(self) -> int:
        """Compute copy number of this ELFRItem, i.e. how many other objects of the same type and name there are."""

        items_with_the_same_name = filter(lambda o: o.name == self.name, self.parent.get_all_eflr_items())
        return len(list(items_with_the_same_name)) - 1

    @classmethod
    def _check_parent(cls, parent: "EFLRSet") -> None:
        """Validate a parent EFLRSet instance for this EFLRItem.

        Args:
            parent      :   Parent EFLRSet instance.

        Returns:
            The parent EFLRSet instance.
        """

        if not isinstance(parent, cls.parent_eflr_class):
            raise TypeError(f"Expected an instance of {cls.parent_eflr_class.__name__}; "
                            f"got a {type(parent)}: {parent}")

    @property
    def attributes(self) -> dict[str, Attribute]:
        """Attributes defined for this EFLRItem (sub)class with its values for the current instance."""

        return {key: value for key, value in self.__dict__.items() if isinstance(value, Attribute)}

    def __str__(self) -> str:
        """Description of the EFLRItem instance."""

        return f"{self.__class__.__name__} '{self.name}'"

    def __setattr__(self, key: str, value: Any) -> None:
        """Limit the possibility of setting attributes by excluding Attribute instances.

        This prevents overwriting Attribute instances being attributes of this EFLRItem. ValueError is raised at such
        attempt. If only a value of the Attribute instance is supposed to be changed, the Attribute's 'value' attribute
        should be used instead.
        """

        if isinstance(getattr(self, key, None), Attribute):
            raise RuntimeError(f"Cannot set DLIS Attribute '{key}'. Did you mean setting '{key}.value' instead?")

        return super().__setattr__(key, value)

    @cached_property
    def obname(self) -> bytes:
        """Create OBNAME bytes of this item - bytes used to identify an item in the file.

        They serve as a reference to the current item - e.g. when a Parameter references a Zone.
        """

        return write_struct_obname(self)

    def _make_attrs_bytes(self) -> bytes:
        """Create bytes describing the values of the EFLRItem instance's Attributes."""

        _bytes = b''
        for attr in self.attributes.values():
            if attr.value is None:
                _bytes += b'\x00'
            else:
                _bytes += attr.get_as_bytes()

        return _bytes

    def _run_checks_and_set_defaults(self) -> None:
        """Called before writing the item's bytes. Set default values to some attributes if they were not set at all."""

        pass

    def make_item_body_bytes(self) -> bytes:
        """Create bytes describing the item: its name and values of its attributes."""

        self._run_checks_and_set_defaults()

        return b'p' + self.obname + self._make_attrs_bytes()

    def set_attributes(self, **kwargs: Any) -> None:
        """Set the values and other characteristics of the EFLRItem's attributes.

        Args:
            **kwargs    :   The mapping of attribute names (and parts) on their values to be set.

        This method allows setting 'value', 'units', and 'representation_code' parts of any attribute of
        the item. The expected syntax for the arguments' keys is <attr_name>.<part_name>, e.g.: 'dimension.value',
        'minimum_value.representation_code', 'minimum_value.units'. It is also possible to use only the attribute name
        as the key (e.g. 'dimension', 'maximum_value'); in this case, the 'value' part of the attribute (dimension.value
        or maximum_value.value respectively) is set to the value of the keyword argument.
        """

        def set_value(_attr: Attribute, _value: Any, _key: str = 'value') -> None:
            """Set 'value' or 'units' of the provided Attribute instance."""

            logger.debug(f"Setting {_attr.label}.{_key} of {self} to {repr(_value)}")
            setattr(_attr, _key, _value)

        for attr_name, attr_value in kwargs.items():
            attr = getattr(self, attr_name, None)
            if not attr or not isinstance(attr, Attribute):
                raise AttributeError(f"{self.__class__.__name__} does not have attribute '{attr_name}'")

            if isinstance(attr_value, (dict, AttrSetup)):
                for key, value in attr_value.items():
                    if key not in ('value', 'units'):
                        raise ValueError(f"Cannot set {key} of a(n) {attr.__class__.__name__}")
                    set_value(attr, value, key)

            else:
                set_value(attr, attr_value)

    @staticmethod
    def count_attributes(*attrs: Attribute) -> dict:
        """Count the number of values (length of value list) defined for each of the provided Attribute.

        If no values are defined foe an Attribute, it is not included in the counts dict.
        """

        value_counts = {}
        for attr in attrs:
            if attr.value is not None:
                value_counts[attr.label] = len(attr.value)

        return value_counts


class DimensionedItem:
    """Mixin to be used with EFLRItem subclasses which define 'axis' and 'dimension' Attributes."""

    axis: Attribute
    dimension: "DimensionAttribute"

    def _check_axis_vs_dimension(self) -> None:
        """Check that the number of axes matches the number of dimensions defined for the EFLRItem."""

        axs = self.axis.value
        dims = self.dimension.value

        if axs is None:
            return
        if dims is None:
            return

        if (na := len(axs)) != (nd := len(dims)):
            raise RuntimeError(f"{self}: number of axes ({na}) does not match the number of dimensions ({nd})")

        for i in range(na):
            ac = axs[i].coordinates.value
            if ac is None:
                continue
            if (nc := len(ac)) != dims[i]:
                raise RuntimeError(f"{self}: number of coordinates in axis {i+1} ({nc}) does not match the "
                                   f"dimension {i+1} ({dims[i]})")

    def _check_or_set_value_dimensionality(self, value: Union[list, tuple, None],
                                           value_label: Optional[str] = None) -> None:
        """Determine the dimensionality (shape) of a value. Verify or set up the 'dimension' attr based on that."""

        if value is None:
            return

        value_label = value_label or 'value'

        try:
            arr = np.array(value)
        except ValueError:
            raise RuntimeError(f"{self}: {value_label} {value} does not have a regular dimensionality structure")

        dim_from_value = list(arr.shape[1:])
        if self.dimension.value is not None:
            if dim_from_value != self.dimension.value:
                raise RuntimeError(f"{self}: shape of {value_label} {value} (shape {arr.shape}) does not match "
                                   f"the specified dimensionality: {self.dimension.value}")
        else:
            self.dimension.value = dim_from_value
