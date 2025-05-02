# SesamCommands: Streamlining Sesam Workflows and Local Command Execution

SesamCommands is a comprehensive Python package designed to simplify the development and execution of Sesam workflows on both local and cloud platforms. It provides a suite of executors that streamline the local execution of Sesam commands, allowing developers to invoke commands as if operating from a command-line interface, independent of any workflow context.

This package not only simplifies the development process but also adeptly handles the complexities of command execution involving Sesam Core, Wasim, and Sestra applications. The intricacies of workflow execution and management are taken care of by the OneWorkflow and OneCompute Python packages.

In summary, SesamCommands is an invaluable tool for developers seeking to enhance their productivity and streamline their Sesam workflow development process.

## Usage and Examples

For a more comprehensive understanding and additional examples, please visit the Homepage link provided on this page.

```python
"""Demonstration of executing a SesamCoreCommand as part of a larger workflow using the OneWorkflow client.
This workflow could contain many more commands."""

# Import necessary modules and functions
import asyncio
from dnv.oneworkflow.utils import (
    CommandInfo,
    one_workflow_client,
    run_managed_commands_in_parallel_async,
)
from dnv.sesam.commands import SesamCoreCommand

# Instantiate the OneWorkflow client with workspace ID and path
client = one_workflow_client(
    workspace_id="TestWorkflow", workspace_path=r"C:\MyWorkspace", cloud_run=False
)

# Create an instance of the SesamCoreCommand class, specifying the command, input file name, and options
sesam_core_command = SesamCoreCommand(
    command="uls", input_file_name="input.json", options="-v"
)

# Create an instance of the CommandInfo class, specifying the commands and load case folder name
cmd_info = CommandInfo(
    commands=[sesam_core_command],
    load_case_foldername="LoadCase1",
)

# Run workflow/command asynchronously
asyncio.run(
    run_managed_commands_in_parallel_async(
        client=client,
        commands_info=[cmd_info],
    )
)
```

```python
"""
This script demonstrates how to execute a standalone SesamCoreCommand for FLS aggregation, independent of any workflow context,
similar to running an application from the command line.
"""

import os
from dnv.sesam.commands import SesamCoreCommand
from dnv.sesam.commands.executors import execute_command

working_directory = os.path.join(
    os.getcwd(), "data", "workspace_sesamcore_aggregation", "CommonFiles"
)

score_exe_cmd = SesamCoreCommand(
    working_dir=working_directory,
    command="accumulation accumulate",
    input_file_name="accumulation-input-ElementScreening.json",
    options=" ",
)

execute_command(score_exe_cmd)
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Support

If you encounter any issues, have questions, or want to provide feedback, please get in touch with our support team at software.support@dnv.com. We are committed to continuously improving SesamCommands Python package and providing timely assistance to our users.
