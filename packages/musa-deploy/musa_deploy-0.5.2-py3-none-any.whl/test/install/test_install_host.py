import sys
import os
import pytest
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test.utils import (
    TestInstall,
    is_running_with_root,
)
from musa_deploy.install import DriverPkgMgr, HostPkgMgr, ContainerToolkitsPkgMgr
from musa_deploy.utils import FontGreen


@pytest.mark.skipif(
    not is_running_with_root(), reason="This test needs root permission."
)
def test_install_dkms():
    test_driver_install = TestInstall(DriverPkgMgr)
    test_container_toolkit_install = TestInstall(ContainerToolkitsPkgMgr)
    test_host_install = TestInstall(HostPkgMgr)
    # uninstall dependencies
    test_container_toolkit_install.uninstall()
    test_driver_install.uninstall()
    # uninstall target: dkms
    test_host_install.uninstall()
    # install target: dkms
    mock_input = StringIO("n\n")
    with patch.object(sys, "stdin", mock_input):
        test_host_install.install()
    test_host_install.check_report_includes(
        test_host_install._install_log,
        f"Please choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}\nPlease choose the display manager: {FontGreen('lightdm')}",
    )
