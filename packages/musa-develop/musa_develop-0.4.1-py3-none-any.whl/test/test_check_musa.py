import sys
import os
from musa_develop.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_musa_inside_container():
    tester = TestChecker(CheckModuleNames.musa.name)
    simulation_log = {
        "MUSAToolkits": ("", "", 0),
        "musa_version": ('musa_toolkits:{"version":"3.1.0"}', "", 0),
    }
    musa_ground_truth = "MUSAToolkits                Version: 3.1.0"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(musa_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_musa_inside_container()
