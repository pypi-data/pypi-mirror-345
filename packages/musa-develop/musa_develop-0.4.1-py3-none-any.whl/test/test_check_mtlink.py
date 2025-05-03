import sys
import os
from musa_develop.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


def test_check_mtlink_simulation():
    tester = TestChecker(CheckModuleNames.mtlink.name)
    simulation_log = {"MTLink": ("", "", 0)}
    mtlink_ground_truth = """\
MTLink"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(mtlink_ground_truth)
    tester.test_single_module()


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_mtlink_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.mtlink.name)
    simulation_log = {"MTLink": ("", "", 0)}
    mtlink_ground_truth = """\
MTLink"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(mtlink_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    # test_check_mtlink_simulation()
    test_check_mtlink_simulation_inside_container()
