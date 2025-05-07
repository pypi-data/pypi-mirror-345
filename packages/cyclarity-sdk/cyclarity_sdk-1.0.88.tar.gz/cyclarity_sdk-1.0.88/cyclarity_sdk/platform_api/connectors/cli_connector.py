from cyclarity_sdk.platform_api.Iplatform_connector import IPlatformConnectorApi   # noqa
from cyclarity_sdk.sdk_models import ExecutionMetadata
from cyclarity_sdk.sdk_models import ExecutionState
from cyclarity_sdk.sdk_models.artifacts import TestArtifact
from cyclarity_sdk.sdk_models.findings import Finding
from cyclarity_sdk.sdk_models.findings.models import MessageType, PTFinding
import os
import tempfile
import shutil
from datetime import datetime
from pydantic import BaseModel


class CliConnector(IPlatformConnectorApi):

    def __init__(self, max_size=5000000):
        self.file_paths = {
            'artifact': 'logs/artifact.log',
            'finding': 'logs/finding.log',
            'state': 'logs/state.log',
            'results': 'results/findings.txt',
        }
        self.tmp_path = None
        try:
            self.create_cli_logs_files(self.file_paths)
        except OSError:
            self.tmp_path = tempfile.mkdtemp()
            print(f"Got an error to create log files, trying tmp dir-{self.tmp_path}")
            new_log_paths = {func: f"{self.tmp_path}/{log_path}" for func, log_path in self.file_paths.items()}
            self.create_cli_logs_files(new_log_paths)
            self.file_paths = new_log_paths
        except Exception:
            print("Unable to create log files")
        self.max_size = max_size
        self.execution_metadata = ExecutionMetadata(
            execution_id='CLI',
            test_id='CLI',
            step_id='CLI'
        )

    def __del__(self):
        if self.tmp_path and os.path.exists(self.tmp_path):
            shutil.rmtree(self.tmp_path)

    def create_cli_logs_files(self, file_paths):
        for path in file_paths.values():
            dir_path = os.path.dirname(path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        print(f"log files were created: {file_paths}")

    def get_execution_meta_data(self) -> ExecutionMetadata:
        return self.execution_metadata

    def set_execution_meta_data(self, execution_metadata: ExecutionMetadata):
        self.execution_metadata = execution_metadata

    def _write_to_file(self, file_path, message):
        if os.path.exists(file_path) and os.path.getsize(file_path) > self.max_size:  # noqa
            shutil.move(file_path, file_path + '.' + datetime.now().strftime('%Y%m%d%H%M%S'))
        try:
            with open(file_path, 'a') as f:
                f.write(message + '\n')
        except Exception as e:
            print(f"Error writing to file: {e}")

    def _log(self, function_name, data):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'{timestamp}: {data}'
        self._write_to_file(self.file_paths[function_name], message)
        return message

    def _print_and_log(self, function_name, data):
        message = self._log(function_name, data)
        print(message)

    def send_artifact(self, test_artifact: TestArtifact):
        self._print_and_log('artifact', test_artifact)

    def send_finding(self, finding: Finding):
        if finding.type == MessageType.FINDING:
            self._log('finding', finding)
            f_data: PTFinding = finding.data
            finding_text = f_data.as_text()
            print(finding_text)
            self._write_to_file(self.file_paths['results'], finding_text)
        else:
            self._print_and_log('finding', finding)

    def send_state(self, execution_state: ExecutionState):
        if execution_state.error_message:
            self._print_and_log('state', execution_state)
        else:
            print(f"{execution_state.status.value}: [{execution_state.percentage:3}%]")
            self._log('state', execution_state)

    def publish_runnable_result(self, result: BaseModel):
        self._print_and_log('result', result.model_dump_json())

    def get_output(self, execution_id: str, test_id: str, component_id: str, output_id=None):
        # TODO: implement
        return "Mock"

    def send_data(self, execution_metadata: ExecutionMetadata, data):
        return 201
