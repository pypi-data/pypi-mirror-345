import sys
import os
from musa_develop.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, GREEN_PREFIX, COLOR_SUFFIX, set_env


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_mtml_sgpu_toolkit_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.container_toolkit.name)
    simulation_log = {
        "container_toolkit": ("", "", 0),
        "sgpu_dkms": ("", "", 0),
        "mtml": ("", "", 0),
    }
    mtml_ground_truth = f"""\
container_toolkit
    - status: \x1b[91mUNKNOWN\x1b[0m
    - {GREEN_PREFIX}Recommendation{COLOR_SUFFIX}: The command 'musa-develop' is currently being executed inside a container. To check container_toolkit, please run the command outside the container."""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(mtml_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_mtml_sgpu_toolkit_simulation_inside_container()
