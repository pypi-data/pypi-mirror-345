import hashlib
from datetime import datetime
from typing import Any, Dict

from mhdwriter.args import WriteArgs, WriteType


def generate_header(args: WriteArgs) -> Dict[str, Any]:
    """
    Generate a .mhd file for a mhd/raw pair.

    Args:
        args (WriteArgs): WriteArgs object specifying parameters for the MHD header creation.

    Returns:
        dict: Returns an ordrered dictionary of relevant metadata key->value pairs.

    """

    assert type(args) == WriteArgs, "Invalid WriteArgs"

    if isinstance(args.date_time, str):
        study_date_time = parse_datetime(args.date_time)
    else:
        study_date_time = args.date_time
    if not args.is_rgb and args.write_type == WriteType.NONE:
        args.write_type = WriteType.RAW

    is_multi = True if args.write_type == WriteType.NONE else False

    raw_name = args.series_description + ".raw"
    raw_name = raw_name.replace(" ", "_")
    if args.write_type == WriteType.RAW_COMPRESSED:
        raw_name += ".gz"
    pixel_sz = _pixel_size(args.fov.upper()) * (2 ** args.downsample_factor)
    pixel_sz = round(pixel_sz, 5)
    metadata = {
        "ObjectType": "Image",
        "NDims": 3,
        "BinaryData": True,
        "BinaryDataByteOrderMSB": False,
        "Modality": "CFT",
        "ManufacturersModelName": "Xerra",
        "TransformMatrix": "-1 0 0 0 -1 0 0 0 -1",
        "Offset": f"{round(pixel_sz * args.width, 3)} {round(pixel_sz * args.height, 3)} {round(float(pixel_sz) * args.length, 3)}",
        "CenterOfRotation": "0 0 0",
        "AnatomicalOrientation": "RAI",
        "ElementSpacing": f"{pixel_sz} {pixel_sz} {pixel_sz}",
        "DimSize": f"{args.width} {args.height} {args.length}",
        "FOV": args.fov,
        "PatientsName": f"{args.study_description}{' ' + args.roi if hasattr(args, 'roi') and args.roi else ''}",
        "PatientID": f"{args.study_description}{' ' + args.roi if hasattr(args, 'roi') and args.roi else ''}",
        "StudyID": args.study_description,
        "StudyDescription": args.protocol,
        "SeriesDescription": args.series_description,
        "Protocol": args.protocol,
        "StudyDate": study_date_time.strftime("%Y%m%d"),
        "StudyTime": study_date_time.strftime("%H%M%S"),
    }

    metadata = _setup_uids(metadata, args.root_site_id)
    if args.write_type == WriteType.RAW_COMPRESSED:
        metadata["CompressedData"] = True
        metadata["CompressedDataSize"] = 9999999999999

    if args.is_rgb:
        metadata["ShowRGB"] = 1
        if not args.write_type == WriteType.NONE:
            metadata["ElementNumberOfChannels"] = 3
            if args.mhd:
                metadata["ElementType"] = "MET_UCHAR"
            else:
                metadata["ElementType"] = "MET_UCHAR_ARRAY"
                metadata["ElementDataFile"] = "LOCAL"
        else:
            metadata["ElementType"] = "MET_UCHAR"
    elif args.is_hdr == "float32":
        metadata["ElementType"] = "MET_FLOAT"
    else:
        metadata["ElementType"] = "MET_USHORT"
        if not args.mhd:
            metadata["ElementDataFile"] = "LOCAL"

    if is_multi:
        metadata["ElementDataFile"] = "slice_%04d.jpg 0 " + str(args.length) + " 1"
    elif args.mhd:
        metadata["ElementDataFile"] = raw_name
    return metadata


def _pixel_size(fov: str) -> float:
    fov = fov.upper()
    fov = fov.replace("FOV", "")
    fov = fov.replace(" ", "")
    xy = 0.00
    if fov == "A":
        xy = 0.020
    elif fov == "B":
        xy = 0.025
    elif fov == "C":
        xy = 0.035
    elif fov == "D":
        xy = 0.045
    elif fov == "E":
        xy = 0.055
    return xy


def _setup_uids(metadata_dict: dict[str, Any], root_site_id: str) -> Dict:
    patients_name = metadata_dict.get("PatientsName", "")
    patients_id = metadata_dict.get("PatientID", "")
    study_id = metadata_dict.get("StudyID", "")
    study_date = int(metadata_dict.get("StudyDate", 20000000))
    study_time = int(metadata_dict.get("StudyTime", 0))
    study_description = metadata_dict.get("StudyDescription", "")
    series_description = metadata_dict.get("SeriesDescription", study_description)
    hash_str = f"{patients_name}{patients_id}{study_id}{study_description}"
    m = hashlib.md5(hash_str.encode()).hexdigest()
    id0 = int(m[0:6], base=16)
    id1 = int(m[-4:], base=16)
    uid_series = hashlib.md5(f"{m}{series_description}".encode()).hexdigest()
    uid_series_int = int(uid_series[0:6], base=16)
    uid_image = int(hashlib.md5(f"{uid_series}1".encode()).hexdigest()[0:6], base=16)
    metadata_dict[
        "StudyInstanceUID"
    ] = f"{root_site_id}.{id0}.{id1}.{study_date - 20000000}.{study_time}.1"
    metadata_dict[
        "SeriesInstanceUID"
    ] = f"{root_site_id}.{id0}.{uid_series_int}.{study_date - 20000000}.{study_time}.2"
    metadata_dict[
        "SOPInstanceUID"
    ] = f"{root_site_id}.{id0}.{uid_image}.{study_date - 20000000}.{study_time}.3"
    metadata_dict["SeriesDate"] = metadata_dict["StudyDate"]
    metadata_dict["SeriesTime"] = metadata_dict["StudyTime"]
    return metadata_dict


def parse_datetime(date_string) -> datetime:
    formats = ["%Y-%m-%d-%H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"time data '{date_string}' does not match expected formats")
