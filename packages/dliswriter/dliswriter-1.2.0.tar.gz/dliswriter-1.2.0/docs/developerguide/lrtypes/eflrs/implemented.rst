.. _Implemented EFLRs:

Implemented EFLR objects
~~~~~~~~~~~~~~~~~~~~~~~~
The types of :ref:`EFLRs <EFLRs>` implemented in this library are described below.
Note: the standard defines several more types of EFLRs.


.. _File Header:

File Header
^^^^^^^^^^^
Every Logical File must have a (single) File Header.
Its length must be exactly 124 bytes.
The ``identifier`` attribute of the File Header represents the name of the DLIS file.
It should be a string of max 65 characters.


.. _Origin:

Origin
^^^^^^
Every Logical File file must contain at least one Origin. Usually, it immediately follows the `File Header`_.
The Origin keeps key information related to the scanned well, the scan procedure, producer, etc.
The ``creation_time`` :ref:`Attribute <Attribute>` of Origin, if not explicitly specified, is set to the current
date and time (when the object is initialised).

The ``origin_reference`` :ref:`Attribute <Attribute>` of an Origin (assigned by user or automatically generated) is used
as an Origin reference in other DLIS objects. By default, the ``origin_reference`` of the first defined Origin is assigned to
all other objects of its Logical File.

To indicate that an object originally comes from a different logical file, the user should create another Logical File,
an Origin for it its defining origin additional Origin
with the relevant information and pass its ``file_set_number`` when creating the objects belonging to that Origin.

From RP66:
    ORIGIN Objects uniquely identify Logical Files and describe the basic circumstances under which Logical Files
    are created. ORIGIN Objects also provide a means for distinguishing different instances of a given entity.
    Each Logical File must contain at least one ORIGIN Set, which may contain one or more ORIGIN Objects.
    The first Object in the first ORIGIN Set is the Defining Origin for the Logical File in which it is contained,
    and the corresponding Logical File is called the Origin’s Parent File.
    It is intended that no two Logical Files will ever have Defining Origins with all Attribute Values identical.


.. _Channel:

Channel
^^^^^^^
Channel is meant for wrapping and describing data sets.
A single channel refers to a single column of data (a single curve, e.g. depth, time, rpm)
or a 2D data set (an image, e.g. amplitude, radius).

From RP66:
    Channel Objects (...) identify Channels and specify their properties and their representation in Frames.
    The actual Channel sample values are recorded in Indirectly Formatted Logical Records, when present.

In the standard, Channel does not directly contain the data it refers to, but rather described
the data's properties, such as the unit and representation code.

The dimension and element limit express the horizontal shape of the data, i.e. the number of columns.
It is always a list of integers. List of any length would be accepted, but because this implementation
only handles 1D and 2D data, this is always a single-element list: ``[1]`` for 1D datasets
and ``[n]`` for 2D datasets, where ``n`` is the number of columns in the image (usually 128).
In this implementation, dimension and element limit should have the same value.
Setting one at initialisation of Channel automatically sets up the other in the same way.

A `Frame`_ always refers to a list of channels. The order is important; the first channel
is used as the index. When a row of data is stored (wrapped in a :ref:`Frame Data` object),
the order of channels as passed to the Frame is preserved.

Channels can also be referred to by `Splice`_, `Path`_, `Calibration`_,
`Calibration Measurement`_, `Process`_, and `Tool`_.

On the receiving end, Channel can reference an `Axis`_ and/or a `Long Name`_.


.. _Frame:

Frame
^^^^^
Frame is a collection of `Channel`_ s. It can be interpreted as a table of numerical data.
Channels can be viewed as variable-width, vertical slices of a Frame.
Information contained in the Frame (and Channels) is used to generate :ref:`Frame Data` objects,
which are horizontal slices of Frame - this time, strictly one row per slice.

Frame has an ``index_type`` :ref:`Attribute <Attribute>`, which defines the kind of data used as the common index
for all (other) channels in the Frame. The values explicitly allowed by standard are:
``ANGULAR-DRIFT``, ``BOREHOLE-DEPTH``, ``NON-STANDARD``, ``RADIAL-DRIFT``, and ``VERTICAL-DEPTH``.
However, because most readers accept other expressions for index type, this library also allows it,
only issuing a warning in the logs.

If the ``index_type`` is defined, this means that the first Channel in the Frame will be interpreted as its index.
If it is absent (left at the default value of ``None``), the Frame is implicitly indexed by the row number instead.

**Note**: in some DLIS viewer software
(e.g the `Schlumberger's Log Data Composer <https://schlumberger-log-data-toolbox.software.informer.com/>`_),
Frame index is required to be strictly regularly spaced, i.e. the difference between the consecutive values in the
index must be the same across the dataset. If the data of the channel which is supposed to be used as the index
are not regularly spaced, it might be beneficial to switch to the implicit row-number indexing by removing
the ``index_type`` specification. The writer issues a warning in the log messages if such irregularity is detected.

Additional metadata defining a Frame can include its ``direction`` (``INCREASING`` or ``DECREASING``),
``spacing`` (a float value + unit), as well as ``index_max`` and ``index_min``.
These values are needed for some DLIS viewers to interpret the data correctly.
Therefore, if not explicitly specified by the user, these values are inferred from the data:
either from the first channel (if ``index_type`` is specified) or from the data size (for row-number indexing).

Frame can be referenced by `Path`_.

From RP66:
    A Frame constitutes the Indirectly Formatted Data of a Type FDATA Indirectly Formatted Logical Record (IFLR).
    The Data Descriptor Reference of the FDATA Logical Record refers to a Frame Object (...)
    and defines the Frame Type of the Frame.
    Frames of a given Frame Type occur in sequences within a single Logical File.
    A Frame is segmented into a Frame Number, followed by a fixed number of Slots that contain Channel samples,
    one sample per Slot. The Frame Number is an integer (Representation Code UVARI) specifying the numerical order
    of the Frame in the Frame Type, counting sequentially from one. All Frames of a given Frame Type record the same
    Channels in the same order. The IFLRs containing Frames of a given Type need not be contiguous.

    A Frame Type may or may not have an Index Channel. If there is an Index Channel, then it must appear first
    in the Frame and it must be scalar. When an Index Channel is present, then all Channels in the Frame are assumed
    to be "sampled at" the Index value. For example, if the Index is depth, then Channels are sampled at the given
    depth; if time, then they are sampled at the given time, etc. (...)

    The truth of the assumption just stated is relative to the measuring and recording system used and does not
    imply absolute accuracy. For example, depth may be measured by a device that monitors cable movement
    at the surface, which may differ from actual tool movement in the borehole. Corrections that are applied
    to Channels to improve the accuracy of measurements or alignments to indices are left to the higher-level
    semantics of applications.

    When there is no Index Channel, then Frames are implicitly indexed by Frame Number.

    (...)

    Within a Logical File, no two Frame Objects may reference the same Channel Object.
    Informally, this means that if the same "Channel" is to be recorded in two distinct Frame Types in a Logical File,
    then the Channel must be represented by two distinct Channel Objects (...).

    (...)

    If Attribute Index-Type is absent, then there is no Index Channel and Attributes Direction and Spacing are
    meaningless and are ignored. When Attribute Index-Type is absent, then Frames are implicitly indexed by the Frame
    Number. When a Frame has an Index, then it must be the first Channel in the Frame, and it must be scalar.

    (...)

    The DIRECTION Attribute; specifies the behavior of the signed value of the Index.
    If this Attribute is absent, then Index direction is unknown or irrelevant.

    (...)

    The Spacing Attribute; can be used to indicate a constant spacing of the Index from one Frame to the next.
    Its value is the signed difference of the later minus the earlier Index between any (and every) two successive
    Frames of a given Frame Type. Thus, the Spacing Attribute is negative if the Index is decreasing (e.g., an up log)
    and is positive if the Index is increasing (e.g., a down log). Note that when Attribute Spacing is present,
    then Attribute Direction is not required.
    Presence of this Attribute guarantees to the Consumer that Index spacing will be constant for the current Frame Type
    throughout the Logical File. If the Index spacing is allowed to change, then this Attribute must be absent.

    (...)

    INDEX-MIN Attribute specifies the minimum value of the Index Channel in all Frames of the Frame Type.
    If there is no Index Channel, then this is the minimum Frame Number, namely 1.

    (...)

    The INDEX-MAX Attribute specifies the maximum value of the Index Channel in all Frames of the Frame Type.
    If there is no Index Channel, then this is the number of Frames in the Frame Type.


.. _Axis:

Axis
^^^^
Axis defines coordinates (expressed either as floats or strings, e.g ``"40 23' 42.8676'' N"`` is a valid coordinate)
and spacing. Axis can be referenced by `Calibration Measurement`_,
`Channel`_, `Parameter`_, and `Computation`_.

From RP66:
    An Axis Logical Record is an Explicitly Formatted Logical Record that contains information
    describing the coordinate axes of arrays.


.. _Calibration Coefficient:

Calibration Coefficient
^^^^^^^^^^^^^^^^^^^^^^^
Calibration Coefficient describes a set of coefficients together with reference values and tolerances.
It can be referenced by `Calibration`_.

From RP66:
    Calibration-Coefficient Objects record coefficients, their references, and tolerances
    used in the calibration of Channels.


.. _Calibration Measurement:

Calibration Measurement
^^^^^^^^^^^^^^^^^^^^^^^
Calibration Measurement describes measurement performed for the purpose of calibration.
It can reference a `Channel`_ object and can be referenced by `Calibration`_.

From RP66:
    Calibration-Measurement Objects record measurements, references, and tolerances used to compute
    calibration coefficients.


.. _Calibration:

Calibration
^^^^^^^^^^^
Calibration object describes a calibration with performed measurements (`Calibration Measurement`_)
and associated coefficients (`Calibration Coefficient`_). It can also reference
`Channel`_ s and `Parameter`_ s.
The ``method`` of a calibration is a string description of the applied method.

From RP66:
    Calibration Objects identify the collection of measurements and coefficients that participate
    in the calibration of a Channel.


.. _Computation:

Computation
^^^^^^^^^^^
A Computation can reference an `Axis`_, `Zone`_ s, and a `Long Name`_ .
Additionally, through ``source`` :ref:`Attribute <Attribute>`, it can reference another object being the direct source
of this computation, e.g. a `Tool`_.
Computation can be referenced by a `Process`_.

The number of values specified for the ``values`` :ref:`Attribute <Attribute>` must match the number of `Zone`_ s
added to the Computation (through ``zones`` :ref:`Attribute <Attribute>`).

From RP66:
    Computation Objects (...) contain results of computations that are more appropriately expressed as Static
    Information rather than as Channels. Computation Objects are similar to Parameter Objects, except that
    Computation Objects may be associated with Property Indicators, and Computation Objects may be the output
    of PROCESS Objects (...).


.. _Equipment:

Equipment
^^^^^^^^^
Equipment describes a single part of a `Tool`_, specifying its trademark name, serial number, etc.
It also contains float data on parameters such as: height, length, diameter, volume, weight,
hole size, pressure, temperature, radial and angular drift.
Each of these values can (and should) have a unit assigned.

From RP66:
    Equipment Objects (...) specify the presence and characteristics of surface and downhole equipment
    used in the acquisition of data. The purpose of this Object is to record information about individual pieces
    of equipment of any sort that is used during a job. The Tool Object (...) provides a way to collect equipment
    together in ensembles that are more readily recognizable to the Consumer.


.. _Group:

Group
^^^^^
A Group can refer to multiple other :ref:`EFLR <EFLRs>` objects of a given type.
It can also keep references to other groups, creating a hierarchical structure.


.. _Long Name:

Long Name
^^^^^^^^^
Long Name specifies various string attributes of an object to describe it in detail.
It can be referenced by `Channel`_, `Computation`_, or `Parameter`_.

From RP66:
    Long-Name Objects represent structured names of other Objects.
    A Long–Name Object is referenced by (an Attribute of) the Object of which it is the structured name.
    There are standardized Name Part Types corresponding to the Labels of the Attributes of the Long-Name Object.
    For each Name Part Type there is a dictionary-controlled Lexicon of Name Part Values.
    A Name Part Value is a word or phrase. The Long Name is built by selecting those Name Part Types
    that are applicable to an Object and then selecting for each Name Part Type one or more Name Part Values
    from the corresponding Lexicons.


.. _Message:

Message
^^^^^^^
A Message is a string value with associated metadata - such as time
(``datetime`` or float - number of minutes/seconds/etc. since a specific event),
borehole/radial/angular drift, and vertical depth.


.. _Comment:

Comment
^^^^^^^
A Comment is simpler than a `Message`_ object; it contains only the comment text.


.. _No-Format:

No-Format
^^^^^^^^^
No-Format is a metadata container for unformatted data :ref:`No-Format Frame Data`.
It allows users to write arbitrary bytes of data.
Just like `Frame`_ can be thought of as a collection of :ref:`Frame Data` objects,
No-Format is a collection of :ref:`No-Format Frame Data` objects.

No-Format specifies information such as consumer name and description of the associated data.

From RP66:
    Unformatted Data Logical Records are Indirectly Formatted Logical Records of Type NOFORM that contain
    "packets" of unformatted (in the DLIS sense) binary data. The Data Descriptor reference of the NOFORM
    Logical Record refers to a NO-FORMAT Object (...). The purpose of Unformatted Data Logical Records is
    to transport arbitrary data that is of value to the Consumer, the format of which is known by the Consumer,
    but which has no DLIS Semantic meaning.

    NO-FORMAT Objects identify packet sequences of unformatted binary data. The Indirectly Formatted Data field
    of each NOFORM IFLR that references a given No-Format Object contains a segment of the source stream
    of unformatted data. This source stream is recovered by concatenating these segments in the same order
    in which they occur in the NOFORM IFLRs. Each segment of the source stream is considered under the DLIS
    to be a sequence of bytes, and no conversion is applied to the bytes as they are placed into the IFLRs
    nor as they are removed from the IFLRs.


.. _Parameter:

Parameter
^^^^^^^^^
A Parameter is a collection of values, which can be either numbers or strings.
It can reference `Zone`_, `Axis`_, and `Long Name`_.
It can be referenced by `Calibration`_, `Process`_, and `Tool`_.

From RP66:
    Parameter Objects (...) specify Parameters (constant or zoned) used in the acquisition and processing of data.
    Parameters may be scalar-valued or array-valued. When they are array-valued, the semantic meaning
    of the array dimensions is defined by the application.


.. _Path:

Path
^^^^
Path describes several numerical values - such as angular/radial drift and measurement offsets -
of the well. It can also reference a `Frame`_, `Well Reference Point`_,
and `Channel`_ s.

From RP66:
    Path Objects specify which Channels in the Data Frames of a given Frame Type are combined to define part or all
    of a Data Path, and what variations in alignment exist.
    The Index of a Frame Type automatically and explicitly serves as a Locus component of any Data Path represented
    in the Frame Type whenever Frame Attribute INDEX-TYPE has one of the values angular-drift, borehole-depth,
    radial-drift, time, or vertical-depth.


.. _Process:

Process
^^^^^^^
A Process combines multiple other objects: `Channel`_ s, `Computation`_ s,
and `Parameter`_ s.

From RP66:
    [Each Process] describes a specific process or computation applied to input Objects to get output Objects.

The ``status`` :ref:`Attribute <Attribute>` of Process can be one of: ``COMPLETE``, ``ABORTED``, ``IN-PROGRESS``.


.. _Splice:

Splice
^^^^^^
A Splice relates several input and output `Channel`_ s and `Zone`_ s.

From RP66:
    Splice Objects describe the process of concatenating two or more instances of a Channel
    (e.g., from different runs) to get a resultant spliced Channel.


.. _Tool:

Tool
^^^^
A Tool is a collection of `Equipment`_ objects (stored in the ``parts`` :ref:`Attribute <Attribute>`).
It can also reference `Channel`_ s and `Parameter`_ s,
and can be referenced by `Computation`_.

From RP66:
    Tool Objects (...) specify ensembles of equipment that work together to provide specific measurements
    or services. Such combinations are more recognizable to the Consumer than are their individual pieces.
    A typical tool consists of a sonde and a cartridge and possibly some appendages such as centralizers
    and spacers. It is also possible to identify certain pieces or combinations of surface measuring equipment
    as tools.


.. _Well Reference Point:

Well Reference Point
^^^^^^^^^^^^^^^^^^^^
Well Reference Point can be used to specify up to 3 coordinates of a point. The coordinates
should be expressed as floats.
Well Reference Point can be referenced by `Path`_.

From RP66:
    Each well has a Well Reference Point (WRP) that defines the origin of the well’s spatial coordinate system.
    The Well Reference Point is a fixed point in space defined for each Origin. This point is defined relative
    to some permanent structure, such as ground level or mean sea level. It need not coincide with the permanent
    structure, but its vertical distance from the permanent structure must be stated. (...)
    Spatial coordinates of a well are depth, Radial Drift, and Angular Drift. Depth is defined in terms of
    Borehole Depth or Vertical Depth.


.. _Zone:

Zone
^^^^
A zone specifies a single interval in depth or time.
The ``domain`` of a Zone can be one of: ``BOREHOLE-DEPTH``, ``TIME``, ``VERTICAL-DEPTH``.
The expression of ``minimum`` and ``maximum`` of a Zone depends on the domain.
For ``TIME``, they could be ``datetime`` objects or floats (indicating the time since a specific event;
in this case, specifying a time unit is also advisable).
For the other domains, they should be floats, ideally with depth units (e.g. 'm').

Zone can be referenced by `Splice`_, `Process`_, or `Parameter`_.

From RP66:
    Zone Objects specify single intervals in depth or time. Zone Objects are useful for associating other Objects
    or values with specific regions of a well or with specific time intervals.
