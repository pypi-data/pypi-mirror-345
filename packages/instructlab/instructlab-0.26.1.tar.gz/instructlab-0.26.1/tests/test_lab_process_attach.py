# Standard
import datetime
import json
import os

# Third Party
from click.testing import CliRunner

# First Party
from instructlab import lab
from instructlab.defaults import DEFAULTS, ILAB_PROCESS_STATUS


def test_process_attach(
    cli_runner: CliRunner,
):
    # create empty log file, put it in proc reg, and attach for a second
    process_registry = {}
    start_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    process_registry["63866b91-799a-42a7-af02-d0b68fddf19d"] = {
        "pid": 26372,
        "children_pids": [111, 222, 333],
        "type": "Generation",
        "log_file": os.path.join(
            DEFAULTS.LOGS_DIR,
            "generation/generation-63866b91-799a-42a7-af02-d0b68fddf19d.log",
        ),
        "start_time": datetime.datetime.strptime(
            start_time_str, "%Y-%m-%d %H:%M:%S"
        ).isoformat(),
        "status": ILAB_PROCESS_STATUS.RUNNING.value,
    }
    # create registry json, place it in the proper dir
    os.makedirs(exist_ok=True, name=DEFAULTS.INTERNAL_DIR)
    with open(DEFAULTS.PROCESS_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(process_registry, f)
    # list processes and expect output
    os.makedirs(exist_ok=True, name=os.path.join(DEFAULTS.LOGS_DIR, "generation"))
    with open(
        os.path.join(
            DEFAULTS.LOGS_DIR,
            "generation/generation-63866b91-799a-42a7-af02-d0b68fddf19d.log",
        ),
        "w",
        encoding="utf-8",
    ) as _:
        pass  # Do nothing, just create the file
    result = cli_runner.invoke(
        lab.ilab,
        ["--config=DEFAULT", "process", "attach", "--latest"],
    )
    assert result.exit_code == 0
    assert (
        "Attaching to process 63866b91-799a-42a7-af02-d0b68fddf19d. Press Ctrl+C to detach and kill."
        in result.output
    )


def test_process_attach_none(cli_runner: CliRunner):
    # attach to process and expect error
    result = cli_runner.invoke(
        lab.ilab,
        ["--config=DEFAULT", "process", "attach", "--latest"],
    )
    assert result.exit_code == 1, result.output
    assert "No processes found in registry" in result.output
