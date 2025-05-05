from dliswriter import DLISFile, StorageUnitLabel
from dliswriter.logical_record.eflr_types import FileHeaderSet, FileHeaderItem


def make_file_header() -> FileHeaderItem:
    return FileHeaderItem("DEFAULT FHLR", sequence_number=1, parent=FileHeaderSet())


def make_sul() -> StorageUnitLabel:
    return StorageUnitLabel("DEFAULT STORAGE SET", sequence_number=1)


def make_df() -> DLISFile:
    df = DLISFile(storage_unit_label=make_sul())

    lf = df.add_logical_file(file_header=make_file_header())

    lf.add_origin(
        "DEFINING ORIGIN",
        creation_time="2050/03/02 15:30:00",
        file_set_number=1,
        origin_reference=1,
    )
    return df
