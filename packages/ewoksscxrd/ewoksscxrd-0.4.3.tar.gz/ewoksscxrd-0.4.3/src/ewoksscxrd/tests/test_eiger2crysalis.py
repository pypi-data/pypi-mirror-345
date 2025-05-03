import os
import re
import pytest
import fabio
import numpy as np
from ewoksscxrd.tasks.eiger2crysalis import Eiger2Crysalis
from typing import Dict, List, Any


@pytest.fixture
def mock_inputs(tmpdir: pytest.TempdirFactory) -> Dict[str, Any]:
    datadir = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.join(datadir, "data", "eiger_0000.h5")

    return {
        "images": [data_path],
        "processed_output": os.path.join(tmpdir, "test_frame_1"),
        "output": os.path.join(tmpdir, "test_frame_1_{index}.esperanto"),
        "flip_ud": False,
        "flip_lr": True,
        "wavelength": 0.2846,
        "distance": 151.8,
        "beam": [1052, 1102],
        "polarization": 0.99,
        "kappa": 0,
        "alpha": 50,
        "theta": 0,
        "phi": 0,
        "omega": "-36.000000-index*-0.500000",
        "rotation": 180,
        "dummy": -1,
        "offset": 1,
        "dry_run": False,
        "calc_mask": False,
        "custom_frame_set_path": "",
    }


def get_header_content(file_path: str) -> List[str]:
    with open(file_path, "rb") as file:
        content = file.read()
    header_content = content.decode("utf-8", errors="ignore").strip()
    header_parts = re.split(r'\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', header_content)
    return header_parts


def check_header(file_path_1: str, file_path_2: str) -> None:
    header_1 = get_header_content(file_path_1)
    header_2 = get_header_content(file_path_2)

    if len(header_1) != len(header_2):
        raise ValueError(
            f"Header parts count does not match between files:\n{file_path_1}: {len(header_1)} parts\n{file_path_2}: {len(header_2)} parts"
        )

    timestamp_pattern = re.compile(
        r'"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}"'
    )
    for i, (part_1, part_2) in enumerate(zip(header_1, header_2)):
        if i == 64:  # Part 65 is at index 64
            if not (
                timestamp_pattern.match(part_1) and timestamp_pattern.match(part_2)
            ):
                raise ValueError(
                    f"Timestamp part does not match the expected format:\n{file_path_1}: {part_1}\n{file_path_2}: {part_2}"
                )
        else:
            if part_1 != part_2:
                raise ValueError(
                    f"Part {i+1} does not match:\n{file_path_1}: {part_1}\n{file_path_2}: {part_2}"
                )


def check_file_data(file_path_1: str, file_path_2: str) -> None:
    data_1 = fabio.open(file_path_1).data
    data_2 = fabio.open(file_path_2).data
    assert np.allclose(data_1, data_2)


def test_assert_eiger2crysalis(
    tmpdir: pytest.TempdirFactory, mock_inputs: Dict[str, Any]
) -> None:
    datadir = os.path.abspath(os.path.dirname(__file__))
    test_data_path = os.path.join(datadir, "data", "frame_1_1.esperanto")
    task = Eiger2Crysalis(inputs=mock_inputs)
    task.execute()
    generated_file_path = os.path.join(tmpdir, "test_frame_1_1.esperanto")
    check_header(test_data_path, generated_file_path)
    check_file_data(test_data_path, generated_file_path)
