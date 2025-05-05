import os
from typing import Union
import numpy as np
from datetime import datetime

from dliswriter import (
    DLISFile,
    LogicalFile,
)
from dliswriter.logical_record import eflr_types
from dliswriter.utils.enums import (
    Unit,
    Property,
    ZoneDomain,
    EquipmentType,
    EquipmentLocation,
    CalibrationMeasurementPhase,
    ProcessStatus,
)

from tests.dlis_files_for_testing.common import make_file_header, make_sul


def _add_origin(lf: LogicalFile) -> eflr_types.OriginItem:
    origin = lf.add_origin(
        "DEFAULT ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_set_name="Test file set name",
        file_set_number=42,
        origin_reference=42,
        file_number=8,
        run_number=13,
        well_id="5",
        well_name="Test well name",
        field_name="Test field name",
        company="Test company",
    )

    return origin


def _add_frame(
    lf: LogicalFile, *channels: eflr_types.ChannelItem
) -> eflr_types.FrameItem:
    fr = lf.add_frame(
        "MAIN FRAME",
        channels=channels,
        index_type="TIME",
        spacing=0.5,
        encrypted=1,
        description="Frame description",
    )

    fr.spacing.units = Unit.SECOND
    return fr


def _add_channels(
    lf: LogicalFile, ax1: eflr_types.AxisItem, ln: eflr_types.LongNameItem
) -> tuple[eflr_types.ChannelItem, ...]:
    ch = lf.add_channel(
        name="Some Channel",
        dataset_name="image1",
        long_name="Some not so very long channel name",
        properties=[
            Property.AVERAGED,
            Property.LOCALLY_DEFINED,
            Property.SPEED_CORRECTED,
        ],
        cast_dtype=np.float32,
        units=Unit.ACRE,
        dimension=12,
        axis=ax1,
        element_limit=12,
        minimum_value=0,
        maximum_value=127.6,
    )

    ch1 = lf.add_channel(name="Channel 1", dimension=[10, 10], units=Unit.INCH)
    ch2 = lf.add_channel("Channel 2", long_name=ln)
    ch3 = lf.add_channel("Channel 13", dataset_name="amplitude", element_limit=128)
    ch_time = lf.add_channel(
        "posix time", dataset_name="contents/time", units=Unit.SECOND
    )
    ch_rpm = lf.add_channel("surface rpm", dataset_name="contents/rpm", long_name=ln)
    ch_amplitude = lf.add_channel(
        "amplitude", dataset_name="contents/image0", dimension=128
    )
    ch_radius = lf.add_channel(
        "radius", dataset_name="contents/image1", dimension=128, units="in"
    )
    ch_radius_pooh = lf.add_channel(
        "radius_pooh", dataset_name="contents/image2", units=Unit.METER
    )
    ch_x = lf.add_channel(
        "channel_x",
        long_name="Channel not added to the frame",
        dataset_name="image2",
        units="s",
    )

    return (
        ch,
        ch1,
        ch2,
        ch3,
        ch_time,
        ch_rpm,
        ch_amplitude,
        ch_radius,
        ch_radius_pooh,
        ch_x,
    )


def _add_axes(lf: LogicalFile) -> tuple[eflr_types.AxisItem, ...]:
    ax1 = lf.add_axis(
        name="Axis-1", axis_id="First axis", coordinates=list(range(12)), spacing=1
    )
    ax1.spacing.units = Unit.METER

    ax2 = lf.add_axis(
        "Axis-X", axis_id="Axis not added to computation", coordinates=[8], spacing=2
    )
    ax2.spacing.units = "m"

    ax3 = lf.add_axis(name="Axis-3", axis_id="Whatever axis", coordinates=[1, 5.5, 8])

    ax4 = lf.add_axis(name="Axis-4", axis_id="Whatever axis nr 2", coordinates=[-1, 0])

    return ax1, ax2, ax3, ax4


def _add_zones(lf: LogicalFile) -> tuple[eflr_types.ZoneItem, ...]:
    z1 = lf.add_zone(
        name="Zone-1",
        description="BOREHOLE-DEPTH-ZONE",
        domain="BOREHOLE-DEPTH",
        maximum=1300,
        minimum=100,
    )
    z1.maximum.units = "m"
    z1.minimum.units = "m"

    z2 = lf.add_zone(
        "Zone-2",
        description="VERTICAL-DEPTH-ZONE",
        domain=ZoneDomain.VERTICAL_DEPTH,
        maximum=2300.45,
        minimum=200.0,
    )
    z2.maximum.units = Unit.METER
    z2.minimum.units = "m"

    z3 = lf.add_zone(
        "Zone-3",
        description="ZONE-TIME",
        domain=ZoneDomain.TIME,
        maximum="2050/07/13 11:30:00",
        minimum="2050/07/12 9:00:00",
    )

    z4 = lf.add_zone(
        "Zone-4", description="ZONE-TIME-2", domain="TIME", maximum=90, minimum=10
    )
    z4.maximum.units = "min"
    z4.minimum.units = Unit.MINUTE

    zx = lf.add_zone(
        name="Zone-X",
        description="Zone not added to any parameter",
        domain="TIME",
        maximum=10,
        minimum=1,
    )
    zx.maximum.units = Unit.SECOND
    zx.minimum.units = Unit.SECOND

    return z1, z2, z3, z4, zx


def _add_parameters(
    lf: LogicalFile, zones: tuple[eflr_types.ZoneItem, ...], ln: eflr_types.LongNameItem
) -> tuple[eflr_types.ParameterItem, ...]:
    p1 = lf.add_parameter(
        name="Param-1",
        long_name="LATLONG-GPS",
        zones=[zones[0], zones[2]],
        values=["40deg 23' 42.8676'' N", "40deg 23' 42.8676'' N"],
    )

    p2 = lf.add_parameter(
        name="Param-2",
        long_name="LATLONG",
        zones=[zones[1], zones[3]],
        dimension=[3],
        values=[[40.395241, 27.792471, 21.23131213], [21, 23, 24]],
    )

    p3 = lf.add_parameter(name="Param-3", long_name=ln, values=[12.5])
    p3.values.units = Unit.METER

    return p1, p2, p3


def _add_equipment(lf: LogicalFile) -> tuple[eflr_types.EquipmentItem, ...]:
    eq1 = lf.add_equipment(
        name="EQ1",
        trademark_name="EQ-TRADEMARKNAME",
        status=1,
        eq_type=EquipmentType.TOOL,
        serial_number="9101-21391",
        location=EquipmentLocation.WELL,
        height=140,
        length=230.78,
        minimum_diameter=2.3,
        maximum_diameter=3.2,
        volume=100,
        weight=1.2,
        hole_size=323.2,
        pressure=18000,
        temperature=24,
        vertical_depth=587,
        radial_drift=23.22,
        angular_drift=32.5,
    )

    eq1.height.units = Unit.INCH
    eq1.length.units = Unit.CENTIMETER
    eq1.minimum_diameter.units = Unit.METER
    eq1.maximum_diameter.units = Unit.METER
    eq1.weight.units = Unit.METRIC_TON
    eq1.hole_size.units = "m"
    eq1.pressure.units = "psi"
    eq1.temperature.units = Unit.DEGREE_CELSIUS
    eq1.vertical_depth.units = "m"
    eq1.radial_drift.units = "m"
    eq1.angular_drift.units = Unit.METER

    eq2 = lf.add_equipment(
        name="EQ2",
        trademark_name="EQ-TRADEMARKNAME",
        status=0,
        eq_type=EquipmentType.TOOL,
        serial_number="5559101-21391",
    )

    eq3 = lf.add_equipment(
        name="EqX",
        trademark_name="EQ-TRADEMARKNAME",
        status=1,
        eq_type="Tool",
        serial_number="12311",
    )

    return eq1, eq2, eq3


def _add_tools(
    lf: LogicalFile,
    equipment: tuple[eflr_types.EquipmentItem, ...],
    parameters: tuple[eflr_types.ParameterItem, ...],
    channels: tuple[eflr_types.ChannelItem, ...],
) -> tuple[eflr_types.ToolItem, ...]:
    t1 = lf.add_tool(
        name="TOOL-1",
        description="SOME TOOL",
        trademark_name="SMTL",
        generic_name="TOOL GEN NAME",
        parts=[equipment[0], equipment[1]],
        status=1,
        channels=[channels[4], channels[6]],
        parameters=[parameters[0], parameters[2]],
    )

    t2 = lf.add_tool(
        name="Tool-X",
        description="desc",
        trademark_name="SMTL",
        generic_name="TOOL GEN NAME",
        parts=[equipment[1]],
        status=0,
        channels=[channels[8]],
        parameters=[parameters[1]],
    )

    return t1, t2


def _add_processes(
    lf: LogicalFile,
    parameters: tuple[eflr_types.ParameterItem, ...],
    channels: tuple[eflr_types.ChannelItem, ...],
    computations: tuple[eflr_types.ComputationItem, ...],
) -> tuple[eflr_types.ProcessItem, ...]:
    p1 = lf.add_process(
        name="Process 1",
        description="MERGED",
        trademark_name="PROCESS 1",
        version="0.0.1",
        properties=[Property.AVERAGED],
        status="COMPLETE",
        input_channels=[channels[7]],
        output_channels=[channels[6], channels[2]],
        input_computations=[computations[0]],
        output_computations=[computations[1]],
        parameters=parameters,
        comments=["SOME COMMENT HERE"],
    )

    p2 = lf.add_process(
        name="Prc2",
        description="MERGED2",
        trademark_name="PROCESS 2",
        version="0.0.2",
        properties=["AVERAGED"],
        status=ProcessStatus.COMPLETE,
        input_channels=[channels[1]],
        output_channels=[channels[2]],
        input_computations=[computations[1], computations[0]],
        parameters=[parameters[0]],
        comments=["Other comment"],
    )

    return p1, p2


def _add_computation(
    lf: LogicalFile,
    axes: tuple[eflr_types.AxisItem, ...],
    zones: tuple[eflr_types.ZoneItem, ...],
    tools: tuple[eflr_types.ToolItem, ...],
    ln: eflr_types.LongNameItem,
) -> tuple[eflr_types.ComputationItem, ...]:
    c1 = lf.add_computation(
        name="COMPT-1",
        long_name="COMPT1",
        properties=[Property.LOCALLY_DEFINED, "AVERAGED"],
        dimension=[3],
        axis=[axes[2]],
        zones=zones[:2],
        values=[[100, 200, 300], [1, 2, 3]],
        source=tools[0],
    )

    c2 = lf.add_computation(
        name="COMPT2",
        long_name=ln,
        properties=["UNDER-SAMPLED", Property.AVERAGED],
        dimension=[2],
        axis=[axes[3]],
        zones=[zones[0], zones[2]],
        values=[[1.5, 2.5], [4.5, 3.2]],
    )

    cx = lf.add_computation(
        name="COMPT-X",
        long_name="Computation not added to process",
        properties=["OVER-SAMPLED"],
        axis=[axes[0]],
        dimension=[12],
        values=[list(range(12, 24))],
    )

    return c1, c2, cx


def _add_splices(
    lf: LogicalFile,
    channels: tuple[eflr_types.ChannelItem, ...],
    zones: tuple[eflr_types.ZoneItem, ...],
) -> tuple[eflr_types.SpliceItem]:
    s = lf.add_splice(
        name="splc1",
        output_channel=channels[6],
        input_channels=[channels[1], channels[2]],
        zones=[zones[0], zones[1]],
    )

    return (s,)


def _add_calibrations(
    lf: LogicalFile,
    axes: tuple[eflr_types.AxisItem, ...],
    channels: tuple[eflr_types.ChannelItem, ...],
    parameters: tuple[eflr_types.ParameterItem, ...],
) -> tuple[
    eflr_types.CalibrationMeasurementItem,
    eflr_types.CalibrationCoefficientItem,
    eflr_types.CalibrationItem,
]:
    cm = lf.add_calibration_measurement(
        name="CMEASURE-1",
        phase=CalibrationMeasurementPhase.BEFORE,
        axis=axes[3],
        measurement_source=channels[1],
        measurement_type="Plus",
        measurement=[[12.2323, 12.2131]],
        sample_count=12,
        maximum_deviation=[[2.2324, 3.121]],
        standard_deviation=[[1.123, 1.1231]],
        begin_time=datetime(year=2050, month=3, day=12, hour=12, minute=30),
        duration=15,
        reference=[[11, 12]],
        standard=[[11.2, 12.2]],
        plus_tolerance=[[2, 2]],
        minus_tolerance=[[1, 2]],
    )
    cm.duration.units = "s"

    cc = lf.add_calibration_coefficient(
        name="COEF-1",
        label="Gain",
        coefficients=[100.2, 201.3],
        references=[89, 298],
        plus_tolerances=[100.2, 222.124],
        minus_tolerances=[87.23, 214],
    )

    c = lf.add_calibration(
        name="CALIB-MAIN",
        calibrated_channels=[channels[1], channels[2]],
        uncalibrated_channels=[channels[6], channels[7], channels[8]],
        coefficients=[cc],
        measurements=[cm],
        parameters=parameters,
        method="Two Point Linear",
    )

    return cm, cc, c


def _add_well_reference_points(
    lf: LogicalFile,
) -> tuple[eflr_types.WellReferencePointItem, ...]:
    w1 = lf.add_well_reference_point(
        name="AQLN WELL-REF",
        permanent_datum="AQLN permanent_datum",
        vertical_zero="AQLN vertical_zero",
        permanent_datum_elevation=1234.51,
        above_permanent_datum=888.51,
        magnetic_declination=999.51,
        coordinate_1_name="Latitude",
        coordinate_1_value=40.395240,
        coordinate_2_name="Longitude",
        coordinate_2_value=27.792470,
    )

    w2 = lf.add_well_reference_point(
        name="WRP-X",
        permanent_datum="pd1",
        vertical_zero="vz20",
        permanent_datum_elevation=32.5,
        above_permanent_datum=100,
        magnetic_declination=112.3,
        coordinate_1_name="X",
        coordinate_1_value=20,
        coordinate_2_name="Y",
        coordinate_2_value=-0.3,
        coordinate_3_name="Z",
        coordinate_3_value=1,
    )

    return w1, w2


def _add_paths(
    lf: LogicalFile,
    frame: eflr_types.FrameItem,
    wrp: eflr_types.WellReferencePointItem,
    channels: tuple[eflr_types.ChannelItem, ...],
) -> tuple[eflr_types.PathItem, ...]:
    path1 = lf.add_path(
        "PATH-1",
        frame_type=frame,
        well_reference_point=wrp,
        value=(channels[0], channels[1], channels[2]),
        borehole_depth=122.12,
        vertical_depth=211.1,
        radial_drift=12,
        angular_drift=1.11,
        time=13,
    )

    path2 = lf.add_path(
        "PATH-2", value=(channels[4],), tool_zero_offset=1231.1, time=11.1
    )

    return path1, path2


def _add_messages(lf: LogicalFile) -> tuple[eflr_types.MessageItem]:
    m = lf.add_message(
        name="MESSAGE-1",
        message_type="Command",
        time=datetime(year=2050, month=3, day=4, hour=11, minute=23, second=11),
        borehole_drift=123.34,
        vertical_depth=234.45,
        radial_drift=345.56,
        angular_drift=456.67,
        text=["Test message 11111"],
    )

    return (m,)


def _add_comments(lf: LogicalFile) -> tuple[eflr_types.CommentItem, ...]:
    c1 = lf.add_comment(name="COMMENT-1", text=["SOME COMMENT HERE"])

    c2 = lf.add_comment(
        name="cmt2", text=["some other comment here", "and another comment"]
    )

    return c1, c2


def _add_no_formats(lf: LogicalFile) -> tuple[eflr_types.NoFormatItem, ...]:
    nf1 = lf.add_no_format(
        name="no_format_1",
        consumer_name="SOME TEXT NOT FORMATTED",
        description="TESTING-NO-FORMAT",
    )

    nf2 = lf.add_no_format(
        name="no_fmt2", consumer_name="xyz", description="TESTING NO FORMAT 2"
    )

    return nf1, nf2


def _add_long_name(lf: LogicalFile) -> eflr_types.LongNameItem:
    ln = lf.add_long_name(
        name="LNAME-1",
        general_modifier=["SOME ASCII TEXT"],
        quantity="SOME ASCII TEXT",
        quantity_modifier=["SOME ASCII TEXT"],
        altered_form="SOME ASCII TEXT",
        entity="SOME ASCII TEXT",
        entity_modifier=["SOME ASCII TEXT"],
        entity_number="SOME ASCII TEXT",
        entity_part="SOME ASCII TEXT",
        entity_part_number="SOME ASCII TEXT",
        generic_source="SOME ASCII TEXT",
        source_part=["SOME ASCII TEXT"],
        source_part_number=["SOME ASCII TEXT"],
        conditions=["SOME ASCII TEXT"],
        standard_symbol="SOME ASCII TEXT",
        private_symbol="SOME ASCII TEXT",
    )

    return ln


def _add_groups(
    lf: LogicalFile,
    channels: tuple[eflr_types.ChannelItem, ...],
    processes: tuple[eflr_types.ProcessItem, ...],
) -> tuple[eflr_types.GroupItem, ...]:
    g1 = lf.add_group(
        name="ChannelGroup",
        description="Group of channels",
        object_list=[channels[1], channels[2]],
    )

    g2 = lf.add_group(
        name="ProcessGroup",
        description="Group of processes",
        object_list=[processes[0], processes[1]],
    )

    g3 = lf.add_group(
        name="MultiGroup", description="Group of groups", group_list=[g1, g2]
    )

    g4 = lf.add_group(
        name="Mixed-group",
        description="Mixed objects",
        object_list=[channels[4], channels[5], processes[1]],
        group_list=[g1, g3],
    )

    return g1, g2, g3, g4


def create_dlis_file_object() -> DLISFile:
    df = DLISFile(storage_unit_label=make_sul())

    lf = df.add_logical_file(file_header=make_file_header())

    _add_origin(lf)

    axes = _add_axes(lf)
    ln = _add_long_name(lf)
    channels = _add_channels(lf, axes[0], ln)
    frame = _add_frame(lf, *channels[4:9])
    zones = _add_zones(lf)
    params = _add_parameters(lf, zones, ln)
    equipment = _add_equipment(lf)
    tools = _add_tools(lf, equipment, params, channels)
    computations = _add_computation(lf, axes, zones, tools, ln)
    processes = _add_processes(lf, params, channels, computations)
    _add_splices(lf, channels, zones)
    _add_calibrations(lf, axes, channels, params)
    wrp = _add_well_reference_points(lf)
    _add_paths(lf, frame, wrp[0], channels)
    _add_messages(lf)
    _add_comments(lf)
    _add_no_formats(lf)
    _add_groups(lf, channels, processes)

    return df


def write_short_dlis(
    fname: Union[str, os.PathLike[str]], data: Union[dict, os.PathLike[str], np.ndarray]
) -> None:
    df = create_dlis_file_object()
    df.write(fname, data=data)
