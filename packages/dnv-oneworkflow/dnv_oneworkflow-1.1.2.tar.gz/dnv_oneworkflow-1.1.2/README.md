# OneWorkflow

OneWorkflow is a Python library for creating and executing workflows on local machine or on the OneCompute cloud platform. This library simplifies the development and management of workflows, providing an easy-to-use interface for handling complex tasks efficiently.

Its rich features empower developers to build workflows that effortlessly handle complex tasks. Whether running workflows on a local machine or utilizing the power of the cloud, OneWorkflow ensures consistent and reliable execution.

This library allows developers to tap into its extensive range of capabilities, including advanced job management, data integration, error handling, and scalability. OneWorkflow simplifies the implementation of intricate workflows, allowing developers to focus on their core objectives while ensuring a smooth end-to-end user experience.

## Usage/Examples

```python
import asyncio

from dnv.onecompute.flowmodel import WorkUnit
from dnv.oneworkflow.composite_executable_command import (
    CompositeExecutableCommand as SequentialCmd,
)
from dnv.oneworkflow.oneworkflowclient import OneWorkflowClient
from dnv.oneworkflow.python_command import PythonCommand

# Create OneWorkflow Client
client = OneWorkflowClient(
    workspace_id="TestWorkflow",
    workspace_path=r"C:\MyWorkspace",
    application_id="ImproveWorkflowWorkerHost",
    executable_name="ImproveFlowWorker",
)

# Authenticate with Veracity
client.login()

# Upload Input Files
client.upload_files()

# Create Commands
pre_process_py_cmd = PythonCommand(filename="preprocessscript.py")
post_process_py_cmd = PythonCommand(filename="postprocessscript.py")
sequential_cmd = SequentialCmd(
    [pre_process_py_cmd, post_process_py_cmd], r"C:\LoadCase"
)

# Create Work Unit
work_unit = (
    WorkUnit(sequential_cmd)
    .input_directory(r"C:\LoadCase")
    .output_directory(r"C:\Results")
)

# Run Workflow
job_id = asyncio.run(client.run_workflow_async(work_unit))
assert job_id is not None, "Job Id is done"

# Download Results & Logs
client.download_job_logs(job_id)
asyncio.run(client.download_result_files_async(job_id))
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Support

If you encounter any issues, have questions, or want to provide feedback, please get in touch with our support team at software.support@dnv.com. We are committed to continuously improving OneWorkflow and providing timely assistance to our users.
