import os

import dnv.net.runtime  # pylint: disable=unused-import # This is needed to setup the CLR

# pylint: disable=relative-beyond-top-level, reimported
from ._app_installer import app_version_info, install_package
from .command_executor import *
from .sima_cmd_executor import *

WORKER_HOST_APP = "OneWorkflowWorkerHost"
app_root_dir = os.path.join(os.environ["LOCALAPPDATA"], "onecompute")

install_package(app_id=WORKER_HOST_APP, app_root_dir=app_root_dir)

version = app_version_info(WORKER_HOST_APP, app_root_dir)
if version is None:
    print(f"ERROR: Failed to get version for {WORKER_HOST_APP}")
else:
    set_assembly_path(os.path.join(app_root_dir, WORKER_HOST_APP, version))
