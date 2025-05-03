import sys
import os
from musa_develop.check.utils import CheckModuleNames

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import TestChecker


def test_check_driver_from_clinfo_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver_Version_From_Clinfo": (
            "Driver Version                                  20241025 release kuae1.3.0_musa3.1.0 c64ecd8ad@20241024",
            "",
            1,
        )
    }
    driver_from_clinfo_ground_truth = """\
Driver_Version_From_Clinfo  Version: 20241025 kuae1.3.0_musa3.1.0"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_from_clinfo_ground_truth)
    tester.test_single_module()


def test_check_driver_version_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            [
                "Driver Version: 1.0.0",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
            ],
            "",
            0,
        )
    }
    driver_ground_truth = "Driver                      Version: 1.0.0"
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


def test_check_driver_mtbios_simulation():
    tester = TestChecker(CheckModuleNames.driver.name)
    simulation_log = {
        "Driver": (
            [
                "Driver Version: 1.0.0",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "MTBios Version: 3.4.3",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Total: 49152MiB",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
                "Product Name: MTT S4000",
            ],
            "",
            0,
        )
    }
    driver_ground_truth = """\
MTBios                      Version: 3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3
                                       3.4.3"""
    tester.set_simulation_log(simulation_log)
    tester.set_module_ground_truth(driver_ground_truth)
    tester.test_single_module()


if __name__ == "__main__":
    # test_check_driver_from_clinfo_simulation()
    test_check_driver_version_simulation()
    # test_check_driver_mtbios_simulation()
