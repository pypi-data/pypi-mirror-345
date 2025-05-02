"""
This module defines the `InfidepWorkUnit`. This is a specialized work unit that
is used to run Infidep calculations in the cloud.
"""

from typing import Optional
from dnv.oneworkflow import ContainerExecutionWorkUnit, OneWorkflowClient

class InfidepWorkUnit(ContainerExecutionWorkUnit):
    """
    A work unit to run Infidep calculations in the cloud.
    """

    def __init__(
        self, 
        input_file_name: str, 
        infidep_version: str, 
        workunit_id: str = "",
        cpu_request: Optional[str] = "0.5",
        cpu_limit: Optional[str] = "1.0",
        memory_request: Optional[str] = "1.5Gi",
        memory_limit: Optional[str] = "2.5Gi",
        tolerations: Optional[str] = None
    ):
        """
        Initializes a new instance of the InfidepWorkUnit class, which runs Infidep calculations
        in the cloud as part of a OneWorkflow workflow.

        Args:
            input_file_name (str): The name of the file that contains the input data.
            infidep_version (str): The version of Infidep to use.
            workunit_id (str): A unique ID for the work unit.
            cpu_request (Optional[str]): The requested CPU resources.
            cpu_limit (Optional[str]): The maximum CPU resources.
            memory_request (Optional[str]): The requested memory resources.
            memory_limit (Optional[str]): The maximum memory resources.
            tolerations (Optional[str]): A semi-colon delimited list of tolerations.

        Note: The CPU and memory requests and limits, and the tolerations are only relevant
        when the container runs in the OneCompute Kubernetes backend. They will be ignored
        if running in Azure Batch.
        """
        super().__init__(
            input_file_name,
            "onecompute.azurecr.io",
            "infidep-worker",
            infidep_version,
            workunit_id,
            cpu_request,
            cpu_limit,
            memory_request,
            memory_limit,
            tolerations
        )
        self.service_name = "Infidep"


def create_infidep_work_unit(
    client: OneWorkflowClient,
    load_case: str,
    infidep_version: str,
    input_file_name: str = "input.json",
) -> InfidepWorkUnit:
    """
    Utility method to create an InfidepWorkUnit with minimal input.

    Args:
        client (OneWorkflowClient): A OneWorkflow client.
        load_case: The name of the directory containing the input files for the load case.
            This should be a sub-directory of `client.load_cases_directory` (defaults to LoadCases).
        infidep_version (str): The version of Infidep to use, e.g. "v1.0.4".
        input_file_name (str): The name of the input file. Defaults to "input.json".
    """
    load_case_directory = f"{client.load_cases_directory}/{load_case}"
    work_unit = (
        InfidepWorkUnit(
            input_file_name=f"{load_case_directory}/{input_file_name}",
            infidep_version=infidep_version,
            workunit_id=load_case,
        )
        .input_directory(load_case_directory)
        .output_directory(f"{client.results_directory}/{load_case}")
    )

    return work_unit
