#!/usr/bin/env python3
"""DataPipe workflow tests for CLIs and simple workflows."""

import subprocess
from pathlib import Path

import pytest
import yaml
from ctapipe.io import TableLoader
from ctapipe.utils import get_dataset_path


def run_cwl(workflow, config=None, cwd=None):
    """Run cwltool on a workflow using subprocess."""
    command = ["cwltool", "--debug", str(workflow)]
    if config is not None:
        command.append(str(config))
    return subprocess.run(command, capture_output=True, text=True, cwd=cwd)


@pytest.mark.verifies_usecase("DPPS-UC-130-1.2.1")
def test_dl0_dl1(tmp_path):
    """Test transformation from DL0 to DL1."""
    values = tmp_path / "values.cfg"
    values.write_text(
        yaml.dump(
            dict(
                dl0="dataset://gamma_prod5.simtel.zst",
                dl1_filename="events.dl1.h5",
            )
        )
    )

    result = run_cwl(
        Path("workflows/process_dl0_dl1.cwl").absolute(), config=values, cwd=tmp_path
    )

    assert result.returncode == 0, result.stderr

    # Now check that the events.dl1.h5 file looks ok.

    out_path = tmp_path / "events.dl1.h5"
    assert out_path.exists()

    with TableLoader(out_path) as loader:
        assert len(loader.read_scheduling_blocks()) > 0

        sub_events = loader.read_subarray_events()
        assert len(sub_events) > 5
        assert "time" in sub_events.colnames

        tel_events = loader.read_telescope_events()
        assert len(tel_events) > 5
        assert "tel_id" in tel_events.colnames
        assert "hillas_width" in tel_events.colnames
        assert "hillas_width" in tel_events.colnames


@pytest.mark.verifies_usecase("DPPS-UC-130-1.2.2")
def test_dl1_dl2_main(tmp_path):
    """Test transformation from DL1 to DL2 up to stereo geometry (main scenario).

    This actually goes from DL0 to DL2, to avoid having to do a separate
    workflows for each step. However, the full workflow is tested in the
    following test.
    """
    values = tmp_path / "values.cfg"
    values.write_text(
        yaml.dump(
            dict(
                dl1="dataset://gamma_prod5.simtel.zst",
                dl2_filename="events.dl2.h5",
            )
        )
    )

    result = run_cwl(
        Path("workflows/process_dl1_dl2.cwl").absolute(), config=values, cwd=tmp_path
    )

    assert result.returncode == 0, result.stderr

    # Now check that the events.dl1.h5 file looks ok.

    out_path = tmp_path / "events.dl2.h5"
    assert out_path.exists()

    with TableLoader(out_path) as loader:
        assert len(loader.read_scheduling_blocks()) > 0

        sub_events = loader.read_subarray_events()
        assert len(sub_events) > 5
        assert "time" in sub_events.colnames
        assert "HillasReconstructor_h_max" in sub_events.colnames


@pytest.mark.xfail
@pytest.mark.verifies_usecase("DPPS-UC-130-1.2.2")
def test_dl1_dl2_extended(tmp_path):
    """Test transformation from DL1 to DL2 with extended reconstruction."""
    pytest.fail("to be implemented")


@pytest.mark.xfail
@pytest.mark.verifies_usecase("DPPS-UC-130-1.2.2")
def test_dl1_dl2_alt_mono(tmp_path):
    """Test transformation from DL1 to DL2 alternate scenario: mono reco."""
    pytest.fail("to be implemented")


@pytest.mark.verifies_usecase("DPPS-UC-130-1.2")
def test_workflow_dl0_dl2_main(tmp_path):
    """Test workflow of 2 steps: DL0 to DL1 followed by DL1 to DL2.

    Note this is only a PARTIAL validation of UC-130-1.2. The rest should be by
    inspection, since it requires a code review.
    """
    dl0_filename = str(get_dataset_path("gamma_prod5.simtel.zst"))

    values = tmp_path / "values.cfg"
    values.write_text(
        yaml.dump(
            {
                "dl0": {"class": "File", "path": dl0_filename},
            }
        )
    )

    result = run_cwl(
        Path("workflows/workflow_dl0_to_dl2.cwl").absolute(),
        config=values,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr

    # Now check that the events.dl1.h5 file looks ok.

    assert (tmp_path / "gamma_prod5.dl1.h5").exists()
    assert (tmp_path / "gamma_prod5.dl2.h5").exists()
