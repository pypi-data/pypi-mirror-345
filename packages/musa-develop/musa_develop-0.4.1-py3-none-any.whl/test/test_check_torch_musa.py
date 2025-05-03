import sys
import os
from musa_develop.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker, set_env


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_pytorch_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "PyTorch_version": [
            ("2.2.0", "", 0),
            ("8ac9b20d4b090c213799e81acf48a55ea8d437d6", "", 0),
        ],
        "PyTorch": ("", "", 0),
    }
    pytorch_ground_truth = """\
PyTorch                     Version: 2.2.0
                              git_version: 8ac9b20d4b090c213799e81acf48a55ea8d437d6"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(pytorch_ground_truth)
    tester.test_single_module()


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_torch_musa_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "Torch_musa_version": [
            ("1.3.0+87a0b4f", "", 0),
            ("87a0b4f61ef93a5b7b14d0ab5ae0286cac8b4023", "", 0),
        ],
        "Torch_musa": ("", "", 0),
    }
    torch_musa_ground_truth = """\
Torch_musa                  Version: 1.3.0+87a0b4f
                              git_version: 87a0b4f61ef93a5b7b14d0ab5ae0286cac8b4023"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(torch_musa_ground_truth)
    tester.test_single_module()


@set_env("EXECUTED_ON_HOST_FLAG", "False")
def test_check_torchvision_simulation_inside_container():
    tester = TestChecker(CheckModuleNames.torch_musa.name)
    simulation_log = {
        "TorchVision_version": [
            ("0.17.2+c1d70fe", "", 0),
            ("c1d70fe1aa3f37ecdc809311f6c238df900dfd19", "", 0),
        ],
        "TorchVision": ("", "", 0),
    }
    torchvision_ground_truth = """\
TorchVision                 Version: 0.17.2+c1d70fe
                              git_version: c1d70fe1aa3f37ecdc809311f6c238df900dfd19"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(torchvision_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    test_check_pytorch_simulation_inside_container()
    # test_check_torch_musa_simulation_inside_container()
    # test_check_torchvision_simulation_inside_container()
