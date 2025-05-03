import io
import os
from cryio import crysalis
import h5py
import numpy as np
import concurrent.futures
import types
from fabio.limaimage import LimaImage
import hdf5plugin
from fabio import nexus


def create_run_file(scans, crysalis_dir, basename):
    """
    Create a Crysalis run file using the provided scans.
    """
    runHeader = crysalis.RunHeader(basename.encode(), crysalis_dir.encode(), 1)
    runname = os.path.join(crysalis_dir, basename)
    runFile = []
    # Expecting scans to be a list of lists; process the first set of scans.
    for omega_run in scans[0]:
        dscr = crysalis.RunDscr(0)
        dscr.axis = crysalis.SCAN_AXIS["OMEGA"]
        dscr.kappa = omega_run["kappa"]
        dscr.omegaphi = 0
        dscr.start = omega_run["omega_start"]
        dscr.end = omega_run["omega_end"]
        dscr.width = omega_run["domega"]
        dscr.todo = dscr.done = omega_run["count"]
        dscr.exposure = 1
        runFile.append(dscr)
    crysalis.saveRun(runname, runHeader, runFile)
    crysalis.saveCrysalisExpSettings(crysalis_dir)


def create_par_file(par_file, processed_data_dir, basename):
    """
    Create a new .par file using the contents of the original.
    Changes any "FILE CHIP" line so that the referenced file ends with '.ccd'.
    """
    new_par = os.path.join(processed_data_dir, basename)
    with io.open(new_par, "w", encoding="iso-8859-1") as new_file:
        with io.open(par_file, "r", encoding="iso-8859-1") as old_file:
            for line in old_file:
                if line.startswith("FILE CHIP"):
                    new_file.write(f"FILE CHIP {basename.replace('.par', '.ccd')} \n")
                else:
                    new_file.write(line)


def read_dataset(file_path):
    """Read dataset from '/entry_0000/measurement/data'."""
    with h5py.File(file_path, "r") as f:
        data = f["/entry_0000/measurement/data"][()]
    return data


def subtract_frame_inplace(frame, scale_factor, dectris_masking_value):
    """
    For each pixel in a frame:
      - If frame[1] > dectris_masking_value, set result = frame0 + frame1 (saturating at max).
      - Otherwise, result = frame0 - scale_factor*frame1 (clipped at 0).
      - Finally, any input pixels that were already max uint32 in either frame0 or frame1
        are forced back to max in the result (propagated).
    """
    # Constants
    max_val = np.iinfo(frame[0].dtype).max  # 2**32 - 1

    # Work in uint64 / int64 to avoid wrap‑around
    img0 = frame[0].astype(np.uint64)
    img1 = frame[1].astype(np.uint64)

    # 1) Compute both branches in wide dtype:
    sub = img0 - scale_factor * img1
    add = img0 + img1

    # 2) Clamp each branch into [0, max_val]
    sub = np.clip(sub, 0, max_val)
    add = np.minimum(add, max_val)

    # 3) Select per‐pixel which branch to use
    mask_thresh = img1 > dectris_masking_value
    result = np.where(mask_thresh, add, sub)

    # 4) Propagate any saturated inputs back to max
    mask_input_max = (frame[0] == max_val) | (frame[1] == max_val)
    result[mask_input_max] = max_val

    # 5) Write back into frame[0], casting to uint32
    frame[0][:] = result.astype(np.uint32)


def subtract_images_inplace_parallel(data, scale_factor, masking_value):
    """
    Processes a 4D dataset in parallel:
      - The input 'data' must have shape (nframes, 2, H, W).
      - Each frame is processed by subtract_frame_inplace with the given scale and threshold.
      - After processing, only image0 is returned as a 3D array.
    """
    if data.ndim != 4:
        raise ValueError("Input data must be 4D.")
    if data.shape[1] < 2:
        raise ValueError("Need at least 2 images along dimension 1.")
    num_frames = data.shape[0]
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        futures = [
            executor.submit(
                subtract_frame_inplace, data[i], scale_factor, masking_value
            )
            for i in range(num_frames)
        ]
        concurrent.futures.wait(futures)

    # Extract the first image across all frames
    result = data[:, 0, :, :]

    # If only one frame is present, remove the frame axis
    if result.shape[0] == 1:
        result = result[0]
    # Squeeze extra dimensions if needed
    if result.ndim != 3:
        result = np.squeeze(result)
    return result


def create_header_from_file(filepath):
    """
    Read an existing NeXus/LIMA HDF5 file at `filepath` and
    build a header dict suitable for write_lima_images().
    """

    def _decode(val):
        if isinstance(val, bytes):
            return val.decode("utf-8")
        return str(val)

    header = {}
    with h5py.File(filepath, "r") as f:
        entry = f["/entry_0000"]

        # Read basic entry metadata
        header["title"] = _decode(entry["title"][()])

        # Determine instrument and detector names
        skip = {"measurement", "program_name", "start_time", "title"}
        inst_name = next(k for k in entry.keys() if k not in skip)
        header["instrument"] = inst_name
        inst_grp = entry[inst_name]

        det_name = next(iter(inst_grp.keys()))
        header["detector"] = det_name
        det_grp = inst_grp[det_name]

        # Acquisition metadata
        acq = det_grp["acquisition"]
        header["exposure_time"] = float(acq["exposure_time"][()])
        header["latency_time"] = float(acq["latency_time"][()])
        if "nb_frames_per_trigger" in acq:
            header["mode"] = _decode(acq["nb_frames_per_trigger"][()])
        else:
            header["mode"] = _decode(acq.get("mode", ""))
        header["trigger_mode"] = _decode(acq["trigger_mode"][()])

        # Detector information
        info = det_grp["detector_information"]
        header["model"] = _decode(info["model"][()])
        header["type"] = _decode(info["plugin"][()])

        pix = info["pixel_size"]
        header["pixel_size_x"] = float(pix["xsize"][()])
        header["pixel_size_y"] = float(pix["ysize"][()])

        # Compute image ROI from data shape
        data = det_grp["data"]
        H, W = data.shape[-2], data.shape[-1]
        header["image_roi"] = f"<0,0>-<{H}x{W}>"

    # Fill defaults for any missing LImA parameters
    defaults = {
        "autoexpo_mode": "",
        "image_bin": "<1x1>",
        "image_flip": "<flip x : False,flip y : False>",
        "image_rotation": "Rotation_0",
        "bin_x": 1,
        "bin_y": 1,
        "flip_x": 0,
        "flip_y": 0,
        "xstart": 0,
        "ystart": 0,
    }
    for key, val in defaults.items():
        header.setdefault(key, val)

    return header


def write_lima_images(result, output_path, header):
    """
    Write the result (3D array: nframes x H x W) as a NeXus HDF5
    file with the following structure:

    /                        (NXroot; file-level attrs)
      entry_0000             (NXentry; attrs + title, start_time, end_time)
        ESRF-ID15B           (NXinstrument; default="eiger")
          eiger              (NXdetector; depends_on=".")
            acquisition     (NXcollection; exposure_time, latency_time,
                            mode, nb_frames, trigger_mode)
            data            (UINT32 dataset shaped nxHxW; interpretation="image")
            detector_information
                           (NXcollection; image_lima_type, model, name, type,
                            pixel_size, max_image_size)
            header          (NXcollection; acq_*, image_*)
            image_operation (NXcollection; binning, dimension, flipping,
                            region_of_interest, rotation)
            plot            (NXdata; signal="data")
        measurement         (NXcollection; data → /…/data)
    """
    img = LimaImage(data=result, header=header)

    def custom_write(self, filename):
        start_time = nexus.get_isotime()
        abs_name = os.path.abspath(filename)
        mode = "w"

        # choose compression
        if hdf5plugin is None:
            compression = {"compression": "gzip", "compression_opts": 1}
        else:
            compression = hdf5plugin.Bitshuffle()

        # open NeXus file
        # WARNING creator needs to start with LIMA to be recognized by Fabio as a Lima Image
        with nexus.Nexus(abs_name, mode=mode, creator="LIMA (Ewoks)") as nxs:

            det_name = header.get("detector", "eiger")

            # ── entry_0000 (NXentry) ─────────────────────────────────────────────
            entry = nxs.new_entry(
                entry="entry",
                program_name=None,
                title=header.get("title", "Ewoks Lima1 detector acquisition"),
                force_time=start_time,
                force_name=False,
            )
            entry.attrs["default"] = f"ESRF-ID15B/{det_name}/plot"

            # ── instrument (NXinstrument) ────────────────────────────────────────
            inst_name = "ESRF-ID15B"  # TODO Bug Lima2 does not write BL name correctly header.get("instrument", "ESRF-ID15B")
            inst_grp = nxs.new_class(entry, inst_name, class_type="NXinstrument")
            inst_grp.attrs["default"] = det_name

            # ── detector (NXdetector) ─────────────────────────────────────────────
            det_grp = nxs.new_class(inst_grp, det_name, class_type="NXdetector")
            det_grp.attrs["depends_on"] = "."

            # compute dims & chunk
            nframes, H, W = self.data.shape
            max_bytes = 4 * 1024**3
            itemsize = self.dtype.itemsize
            max_rows = max(1, int(max_bytes // (itemsize * W)))
            chunk_rows = min(H, max_rows)

            # ── acquisition (NXcollection) ───────────────────────────────────────
            acq = nxs.new_class(det_grp, "acquisition", class_type="NXcollection")
            acq["exposure_time"] = float(header.get("exposure_time", 0.0))
            acq["latency_time"] = float(header.get("latency_time", 0.0))
            acq["mode"] = (
                "Single"  # TODO Bug there are 2 `mode`` in Lima1 files header.get("mode", "Single")
            )
            acq["nb_frames"] = int(nframes)
            acq["trigger_mode"] = header.get("trigger_mode", "ExtTrigSingle")

            # ── data (UINT32 dataset) ────────────────────────────────────────────
            dataset = det_grp.create_dataset(
                "data",
                shape=(nframes, H, W),
                chunks=(1, chunk_rows, W),
                dtype=self.dtype,
                **compression,
            )
            dataset.attrs["interpretation"] = "image"

            # ── detector_information (NXcollection) ─────────────────────────────
            info = nxs.new_class(
                det_grp, "detector_information", class_type="NXcollection"
            )
            info["image_lima_type"] = f"Bpp{8 * itemsize}"
            info["model"] = header.get("model", "Dectris EIGER2 CdTe 9M")
            info["name"] = det_name
            info["type"] = header.get("type", "E-18-0119")

            max_sz = nxs.new_class(info, "max_image_size", class_type="NXcollection")
            max_sz["xsize"] = int(W)
            max_sz["ysize"] = int(H)

            pix = nxs.new_class(info, "pixel_size", class_type="NXcollection")
            pix["xsize"] = (
                0.000075  # TODO Lima2 pixel size is in microns instead of meters float(header.get("pixel_size_x", 0.000075))
            )
            pix["ysize"] = (
                0.000075  # TODO Lima2 pixel size is in microns instead of meters float(header.get("pixel_size_y", 0.000075))
            )

            # ── header (NXcollection) ────────────────────────────────────────────
            hdr = nxs.new_class(det_grp, "header", class_type="NXcollection")
            hdr["acq_autoexpo_mode"] = header.get("autoexpo_mode", "OFF")
            hdr["acq_expo_time"] = str(header.get("exposure_time", "0"))
            hdr["acq_latency_time"] = str(header.get("latency_time", "0"))
            hdr["acq_mode"] = header.get("mode", "Single")
            hdr["acq_nb_frames"] = str(nframes)
            hdr["acq_trigger_mode"] = header.get("trigger_mode", "ExtTrigSingle")
            hdr["image_bin"] = header.get("image_bin", "<1x1>")
            hdr["image_flip"] = header.get(
                "image_flip", "<flip x : False,flip y : False>"
            )
            hdr["image_roi"] = header.get("image_roi", f"<0,0>-<{H}x{W}>")
            hdr["image_rotation"] = header.get("image_rotation", "Rotation_0")

            # ── image_operation (NXcollection) ─────────────────────────────────
            op = nxs.new_class(det_grp, "image_operation", class_type="NXcollection")
            bin_g = nxs.new_class(op, "binning", class_type="NXcollection")
            bin_g["x"] = int(header.get("bin_x", 1))
            bin_g["y"] = int(header.get("bin_y", 1))

            dim_g = nxs.new_class(op, "dimension", class_type="NXcollection")
            dim_g["xsize"] = int(W)
            dim_g["ysize"] = int(H)

            flip_g = nxs.new_class(op, "flipping", class_type="NXcollection")
            flip_g["x"] = int(header.get("flip_x", 0))
            flip_g["y"] = int(header.get("flip_y", 0))

            roi_g = nxs.new_class(op, "region_of_interest", class_type="NXcollection")
            roi_g["xsize"] = int(W)
            roi_g["ysize"] = int(H)
            roi_g["xstart"] = int(header.get("xstart", 0))
            roi_g["ystart"] = int(header.get("ystart", 0))

            op["rotation"] = header.get("image_rotation", "Rotation_0")

            # ── plot (NXdata) ───────────────────────────────────────────────────
            plot = nxs.new_class(det_grp, "plot", class_type="NXdata")
            plot.attrs["signal"] = "data"
            nxs.h5[plot.name].__setitem__("data", h5py.SoftLink(dataset.name))

            # ── measurement (NXcollection) ─────────────────────────────────────
            meas = nxs.new_class(entry, "measurement", class_type="NXcollection")
            nxs.h5[meas.name].__setitem__("data", h5py.SoftLink(dataset.name))

            # ── write frames ────────────────────────────────────────────────────
            for i in range(nframes):
                dataset[i] = self.data[i]

            # ensure default signal is set on entry
            entry.attrs["default"] = plot.name

    img.write = types.MethodType(custom_write, img)
    img.write(output_path)
