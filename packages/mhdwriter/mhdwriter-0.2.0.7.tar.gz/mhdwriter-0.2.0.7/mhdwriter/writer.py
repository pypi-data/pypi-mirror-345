import gzip
import shutil
import threading
from pathlib import Path
from typing import Optional, Any
import imagecodecs as imgc
import cv2
import numpy as np
import zlib

try:
    from tqdm import tqdm

    has_tqdm = True
except:
    has_tqdm = False
from mhdwriter.args import WriteArgs, WriteType
from mhdwriter.header import generate_header


def write_mhd_raw(
        input_dir: Path,
        args: WriteArgs,
        out_path: Optional[Path] = None,
        show_progress: bool = True,
        log_callback: Any = None,
        cancel_event: Optional[threading.Event] = None,
) -> Optional[Path]:
    """
    Convert a stack of files in a directory to a mhd/raw pair.

    Args:
        input_dir (Path): The directory containing the stack of files to convert to a volume.
        args (WriteArgs): WriteArgs object specifying parameters for the MHD header creation.
        out_path (Path): Optional path to specify output directory/file_base. If missing, metadata will be used
            to determine output file/path name in the input_dir.
        cancel_event: optional event to cancel export early

    Returns:
        Optional[Path]: Returns pathlib Path to mhd file upon successful mhd/raw creation, else None.

    """
    if not args.is_rgb and args.write_type == WriteType.NONE:
        args.write_type = WriteType.RAW

    all_files = sorted(list(input_dir.glob("*")))
    all_files = [
        f
        for f in all_files
        if f.is_file() and f.suffix.lower()
           in [".jpg", ".jls", ".jp2", ".jpeg", ".png", ".tif", ".tiff",".jxl"]
    ]
    if len(all_files) == 0:
        print(f"No files found in {input_dir}")
        return None
    ext = all_files[0].suffix.lower()
    file_path = all_files[0]
    try:
        if ext == ".jxl" or ext == ".jls":
            img = imgc.imread(str(file_path))
        else:
            img = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
    except Exception as e:
        print(f"Error reading {str(file_path)}: {e}")
        return None
    args.height, args.width = img.shape[:2]
    if args.downsample_factor > 0:
        dx_factor = 2 ** args.downsample_factor
        if args.skip_files:
            all_files = all_files[::dx_factor]
        args.height = args.height // dx_factor
        args.width = args.width // dx_factor
    args.length = len(all_files)

    if is_cancelled(cancel_event):
        return None

    metadata = generate_header(args)

    if not input_dir.exists():
        raise FileNotFoundError(f"Missing input dir {input_dir}")

    if out_path is None:
        out_path = input_dir

    outfile = None

    if args.write_type == WriteType.NONE:
        out_path = out_path.joinpath(f"{metadata['SeriesDescription']}")
        out_path.mkdir(exist_ok=True, parents=True)
        mhd_path = out_path.joinpath(args.series_description + ".mhd")
        mhdfile = mhd_path.open(mode="w")
        for key in metadata:
            value = metadata[key]
            mhdfile.write(f"{key} = {value}\n")
    else:
        if args.mhd:
            mhd_path = out_path.joinpath(args.series_description + ".mhd")
            out_path = out_path.joinpath(args.series_description + ".raw")
            if mhd_path.exists():
                print(f"File {mhd_path} already exists. Skipping.")
                return
            outfile = out_path.open(mode="wb")
            mhdfile = mhd_path.open(mode="w")
            for key in metadata:
                value = metadata[key]
                mhdfile.write(f"{key} = {value}\n")
        else:
            out_path = out_path.joinpath(args.series_description + ".mha")
            if out_path.exists():
                print(f"File {out_path} already exists. Skipping.")
                return
            outfile = out_path.open(mode="wb")
            for key in metadata:
                value = metadata[key]
                outfile.write(f"{key} = {value}\n".encode('ascii'))
    out_name = out_path.name
    if has_tqdm:
        file_iterator = tqdm(all_files, desc=f"Generating {out_name}") if show_progress else all_files
    else:
        file_iterator = all_files
    if args.write_type == WriteType.RAW_COMPRESSED:
        compressor = zlib.compressobj(level=zlib.Z_BEST_COMPRESSION)
    else:
        compressor = None
    idx = 0
    total = len(all_files)
    shape = None
    last_img = None
    for img_file in file_iterator:
        try:
            if ext == ".jxl" or ext == ".jls":
                img = imgc.imread(str(img_file))
            else:
                img = cv2.imread(str(img_file), cv2.IMREAD_UNCHANGED)
        except Exception as e:
            print(f"Error reading {str(img_file)}: {e}")
            continue
        if img is None:
            print(f"Error reading {str(img_file)}")
            continue
        if shape is None:
            shape = img.shape
        elif shape != img.shape:
            print(f"Shape mismatch: {shape} vs {img.shape}")
            if last_img is None:
                continue
            img = last_img
        else:
            last_img = img
        idx += 1
        if args.is_rgb and not args.write_type == WriteType.NONE:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if args.downsample_factor > 0:
            img = cv2.resize(
                img, (args.width, args.height), interpolation=cv2.INTER_AREA
            )

        if is_cancelled(cancel_event):
            if out_path.exists():
                if args.write_type == WriteType.NONE:
                    shutil.rmtree(out_path)
                else:
                    out_path.unlink()
            return None

        if args.write_type == WriteType.NONE:
            file_path = out_path.joinpath("slice_{0:04d}.jpg".format(idx + 1))
            cv2.imwrite(str(file_path), img)
        else:
            if args.write_type == WriteType.RAW_COMPRESSED:
                squeezed = np.squeeze(img)
                input_bytes = squeezed.tobytes()
                outfile.write(compressor.compress(input_bytes))
            else:
                img.tofile(outfile)
        if log_callback is not None:
            log_callback(f"Processed {out_path.name}: {idx}/{total}")
    if outfile is not None:
        if args.write_type == WriteType.RAW_COMPRESSED:
            try:
                outfile.write(compressor.flush())
            except Exception as e:
                print(f"Error compressing: {e}")
        outfile.close()
    if not out_path.exists():
        return False

    return True


def is_cancelled(stop_val) -> bool:
    if stop_val is None:
        return False
    return stop_val.is_set()
