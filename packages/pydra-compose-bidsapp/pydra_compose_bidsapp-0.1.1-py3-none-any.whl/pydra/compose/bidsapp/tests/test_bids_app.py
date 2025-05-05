import os
import stat
from pathlib import Path
import shutil
import pytest
from fileformats.medimage import NiftiGzX, NiftiGzXBvec
from pydra.compose import bidsapp
from pydra.compose.bidsapp.task import DEFAULT_BIDS_ID
from pydra.utils import asdict
from fileformats.text import Plain as Text
from fileformats.generic import Directory


MOCK_BIDS_APP_NAME = "mockapp"
MOCK_README = "A dummy readme\n" * 100
MOCK_AUTHORS = ["Dumm Y. Author", "Another D. Author"]

BIDS_INPUTS = [
    bidsapp.arg(name="T1w", path="anat/T1w", type=NiftiGzX),
    bidsapp.arg(name="T2w", path="anat/T2w", type=NiftiGzX),
    bidsapp.arg(name="dwi", path="dwi/dwi", type=NiftiGzXBvec),
]
BIDS_OUTPUTS = [
    bidsapp.out(name="whole_dir", type=Directory),  # whole derivative directory
    bidsapp.out(name="a_file", path="file1", type=Text),
    bidsapp.out(name="another_file", path="file2", type=Text),
]


@pytest.mark.xfail(reason="this test will fail until nipype/pydra#822 is merged")
def test_bids_app_docker(
    bids_validator_app_image: str, nifti_sample_dir: Path, work_dir: Path
):

    bids_dir = work_dir / "bids"

    shutil.rmtree(bids_dir, ignore_errors=True)

    TestBids = bidsapp.define(
        bids_validator_app_image,
        inputs=BIDS_INPUTS,
        outputs=BIDS_OUTPUTS,
    )

    task = TestBids(
        **{
            inpt.name: nifti_sample_dir.joinpath(*inpt.path.split("/")).with_suffix(
                inpt.type.ext
            )
            for inpt in BIDS_INPUTS
        }
    )

    result = task(worker="debug")

    for output in BIDS_OUTPUTS:
        assert Path(getattr(result.output, output.name)).exists()


def test_bids_app_naked(
    mock_bids_app_script: str, nifti_sample_dir: Path, work_dir: Path
):

    # Create executable that runs validator then produces some mock output
    # files
    launch_sh = work_dir / "launch.sh"
    # We don't need to run the full validation in this case as it is already tested by test_run_bids_app_docker
    # so we use the simpler test script.
    with open(launch_sh, "w") as f:
        f.write(mock_bids_app_script)

    os.chmod(launch_sh, stat.S_IRWXU)

    TestBids = bidsapp.define(
        launch_sh,
        inputs=BIDS_INPUTS,
        outputs=BIDS_OUTPUTS,
    )

    task = TestBids(
        **{
            i.name: nifti_sample_dir.joinpath(*i.path.split("/")).with_suffix(
                i.type.ext
            )
            for i in BIDS_INPUTS
        },
    )
    outputs = task(worker="debug")

    for output in asdict(outputs).values():
        assert Path(output).exists()
