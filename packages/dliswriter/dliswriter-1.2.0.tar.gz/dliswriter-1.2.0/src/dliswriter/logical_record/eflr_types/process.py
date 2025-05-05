import logging
from typing import Any

from dliswriter.logical_record.core.eflr import EFLRSet, EFLRItem
from dliswriter.logical_record.eflr_types.channel import ChannelSet
from dliswriter.logical_record.eflr_types.computation import ComputationSet
from dliswriter.logical_record.eflr_types.parameter import ParameterSet
from dliswriter.utils.internal.internal_enums import EFLRType
from dliswriter.utils.enums import ProcessStatus
from dliswriter.logical_record.core.attribute import EFLRAttribute, TextAttribute, IdentAttribute, PropertiesAttribute


logger = logging.getLogger(__name__)


class ProcessItem(EFLRItem):
    """Model an object being part of Process EFLR."""

    parent: "ProcessSet"

    def __init__(self, name: str, parent: "ProcessSet", **kwargs: Any) -> None:
        """Initialise ProcessItem.

        Args:
            name        :   Name of the ProcessItem.
            parent      :   Parent ProcessSet of this ProcessItem.
            **kwargs    :   Values of to be set as characteristics of the ProcessItem Attributes.
        """

        self.description = TextAttribute('description')
        self.trademark_name = TextAttribute('trademark_name')
        self.version = TextAttribute('version')
        self.properties = PropertiesAttribute('properties')
        self.status = IdentAttribute(
            'status', converter=ProcessStatus.make_converter("status values"))
        self.input_channels = EFLRAttribute('input_channels', object_class=ChannelSet, multivalued=True)
        self.output_channels = EFLRAttribute('output_channels', object_class=ChannelSet, multivalued=True)
        self.input_computations = EFLRAttribute('input_computations', object_class=ComputationSet, multivalued=True)
        self.output_computations = EFLRAttribute('output_computations', object_class=ComputationSet, multivalued=True)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True)
        self.comments = TextAttribute('comments', multivalued=True)

        super().__init__(name, parent=parent, **kwargs)


class ProcessSet(EFLRSet):
    """Model Process EFLR."""

    set_type = 'PROCESS'
    logical_record_type = EFLRType.STATIC
    item_type = ProcessItem


ProcessItem.parent_eflr_class = ProcessSet
