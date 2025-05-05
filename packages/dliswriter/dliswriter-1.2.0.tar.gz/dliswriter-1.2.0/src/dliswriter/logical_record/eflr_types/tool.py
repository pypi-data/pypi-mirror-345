import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.logical_record.eflr_types.equipment import EquipmentSet
from dliswriter.logical_record.eflr_types.channel import ChannelSet
from dliswriter.logical_record.eflr_types.parameter import ParameterSet
from dliswriter.utils.internal.internal_enums import EFLRType
from dliswriter.logical_record.core.attribute import EFLRAttribute, StatusAttribute, TextAttribute


logger = logging.getLogger(__name__)


class ToolItem(EFLRItem):
    """Model an object being part of Tool EFLR."""

    parent: "ToolSet"

    def __init__(self, name: str, parent: "ToolSet", **kwargs: Any) -> None:
        """Initialise ToolItem.

        Args:
            name        :   Name of the ToolItem.
            parent      :   Parent ToolSet of this ToolItem.
            **kwargs    :   Values of to be set as characteristics of the ToolItem Attributes.
        """

        self.description = TextAttribute('description')
        self.trademark_name = TextAttribute('trademark_name')
        self.generic_name = TextAttribute('generic_name')
        self.parts = EFLRAttribute('parts', object_class=EquipmentSet, multivalued=True)
        self.status = StatusAttribute('status')
        self.channels = EFLRAttribute('channels', object_class=ChannelSet, multivalued=True)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class ToolSet(EFLRSet):
    """Model Tool EFLR."""

    set_type = 'TOOL'
    logical_record_type = EFLRType.STATIC
    item_type = ToolItem


ToolItem.parent_eflr_class = ToolSet
