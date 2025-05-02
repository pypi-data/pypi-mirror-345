"""
This module contains the functions to install a package based on the provided deployment option,
application root directory, and application ID.
"""

import os

import dnv.net.runtime  # pylint: disable=unused-import # This is needed to setup the CLR
from dnv.onecompute.enums import AutoDeployOption
from IPython.core.getipython import get_ipython

from .command_executor import load_clr_type, set_assembly_path


def install_package(
    app_id: str,
    app_root_dir: str = os.path.join(os.environ["LOCALAPPDATA"], "onecompute"),
    deployment_option: AutoDeployOption = AutoDeployOption.RELEASE,
):
    """
    Installs a package based on the provided deployment option, application root directory, and
    application ID.

    Args:
        app_id (str): The ID of the application to be installed.
        app_root_dir (str, optional): The root directory of the application. Defaults to the
            'onecompute'directory in the user's local app data.
        deployment_option (AutoDeployOption, optional): The deployment option to use. Defaults to
            AutoDeployOption.RELEASE.

    Returns:
        None
    """
    # Set the DLLs path
    set_assembly_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dlls"))

    # Get the class types
    app_management_service_type = load_clr_type(
        "DNV.One.Workflow.Deployment.ApplicationEnvironment.ApplicationManagementService, "
        "DNV.One.Workflow.Deployment"
    )
    auto_deployment_type = load_clr_type(
        "DNV.One.Workflow.Deployment.AutoDeployment, DNV.One.Workflow.Deployment"
    )

    # Define the deployment options
    none_option_type = getattr(auto_deployment_type, "None")
    deployment_options = {
        AutoDeployOption.DEV: auto_deployment_type.Development,
        AutoDeployOption.TEST: auto_deployment_type.Test,
        AutoDeployOption.RELEASE: auto_deployment_type.Release,
        AutoDeployOption.NONE: none_option_type,
    }

    # Set the deploy option
    selected_option = deployment_options.get(deployment_option, none_option_type)
    app_manager = app_management_service_type(selected_option, app_root_dir)

    # Install the package
    if is_standard_python_mode():
        install_package_standard(app_manager, app_id)
    else:
        install_package_notebook(app_manager, app_id)


def install_package_standard(app_manager, app_id):
    """
    Checks if an update is available for the specified application ID and installs it if available.

    Args:
        app_id (str): The ID of the application to be installed.
        app_manager: The application manager that handles the deployment of the application.

    Returns:
        None
    """
    update_available = app_manager.IsUpdateAvailable(app_id).Result

    if update_available:
        _ = app_manager.DeployApplication(app_id).Result


def install_package_notebook(app_manager, app_id):
    """
    Checks if an update is available for the specified application ID and installs it if available.
    This function is specifically designed for notebook environments and redirects console output to
    the notebook.

    Args:
        app_id (str): The ID of the application to be installed.
        app_manager: The application manager that handles the deployment of the application.

    Returns:
        None
    """
    string_writer_type = load_clr_type("System.IO.StringWriter, System.IO", True)
    console_type = load_clr_type("System.Console, System", True)

    org_stdout = console_type.Out
    string_writer = string_writer_type()

    console_type.SetOut(string_writer)
    console_type.SetError(string_writer)

    update_available = app_manager.IsUpdateAvailable(app_id).Result
    try:
        if update_available:
            _ = app_manager.DeployApplication(app_id).Result
    except Exception:
        pass
    finally:
        print(string_writer.ToString())
        string_writer.Close()
        console_type.SetOut(org_stdout)


def app_version_info(
    app_id: str,
    app_root_dir: str = os.path.join(os.environ["LOCALAPPDATA"], "onecompute"),
) -> str | None:
    """
    Retrieves the version information of a specified application.

    Args:
        app_id (str): The ID of the application to get the version information for.
        app_root_dir (str, optional): The root directory of the application.
            Defaults to the 'onecompute' directory in the user's local app data.

    Returns:
        str | None: The version ID of the application if it exists, otherwise None.
    """
    # Set the DLLs path
    set_assembly_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dlls"))

    # Get the class types
    app_management_service_type = load_clr_type(
        "DNV.One.Workflow.Deployment.ApplicationEnvironment.ApplicationManagementService, "
        "DNV.One.Workflow.Deployment"
    )
    auto_deployment_type = load_clr_type(
        "DNV.One.Workflow.Deployment.AutoDeployment, DNV.One.Workflow.Deployment"
    )

    # Define the deployment options
    none_option_type = getattr(auto_deployment_type, "None")

    # Create the application manager
    app_manager = app_management_service_type(none_option_type, app_root_dir)

    # Get the application version
    app_version = app_manager.GetApplicationVersionInfo(app_id)
    return app_version.VersionId if app_version else None


def is_standard_python_mode():
    """
    Checks if the current environment is a standard Python interpreter.

    This function attempts to import the `get_ipython` function from the `IPython` module.
    If the import is successful, it checks if the `get_ipython` function returns a non-None
    value. If it does, it means we're running in a Jupyter Notebook environment. Otherwise,
    we're running in a standard Python interpreter.

    Returns:
        bool: True if the current environment is a standard Python interpreter, False otherwise.
    """
    try:
        return get_ipython() is None
    except ImportError:
        return True
