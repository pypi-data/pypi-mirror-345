""" Usage example """

from typing import Optional
from cyclarity_sdk.expert_builder import Runnable, BaseResultsModel
from cyclarity_sdk.sdk_models.findings import PTFinding, FindingType, TestResult
from cyclarity_sdk.sdk_models.findings.types import FindingStatus, TestBasicResultType, KnowledgeOfTarget
import time
from enum import Enum


class CanTestResult(BaseResultsModel):
    res_str: str


class canRunnableInstance(Runnable[CanTestResult]):
    desc: str
    cli_args: str
    _num: Optional[int] = 1  # not appear in the model_json_schema

    def _get_clean_attributes_dict(self, finding_data):
        """
        Cleans and processes a dictionary of attributes:
        - Filters out empty values (except `0`)
        - Converts Enum instances to their `.value`
        - If the Enum value is an object, pretty-prints all its attributes
        - Pretty-prints object attributes if an object is encountered
        """
        finding_att_as_grid = {}

        for key, value in finding_data.items():
            if not value and value != 0:
                continue  # Skip empty values

            # If value is an Enum, check if its value is an object
            if isinstance(value, Enum):
                self.logger.info(f"Enum detected: {value}")

                if hasattr(value.value, "__dict__"):  # If Enum value is an object
                    self.logger.info(f"Enum value is an object: {type(value.value).__name__}")
                    value = self._format_object(value.value)
                else:
                    value = value.value  # Regular Enum, get its actual value

            # If value is a regular object with attributes, pretty-print it
            elif hasattr(value, "__dict__"):
                self.logger.info(f"Object detected: {type(value).__name__}")
                value = self._format_object(value)

            finding_att_as_grid[key] = value

        return finding_att_as_grid

    def _format_object(self, obj):
        """Helper function to format object attributes in a structured way."""
        attributes = vars(obj)  # Get object attributes
        formatted_str = "\n".join(f"{k}: {v}" for k, v in attributes.items())  # Pretty-print each attribute on a new line
        return formatted_str

    def setup(self):
        self.logger.info("setup")

    def run(self) -> CanTestResult:

        # example usage for send_test_description API function
        self.platform_api.send_test_report_description(
            "This is dummy description for test"
        )

        # example usage for reporting test progress
        for percentage in range(101):
            self.platform_api.report_test_progress(percentage=percentage)
            time.sleep(0.01)

        # example usage for sending test findings
        pt_finding = {"topic": "test",
                      "type": FindingType.FINDING,
                      "purpose": "test",
                      "empty_none": None,
                      "empty_string": '',
                      "zero_val": 0,
                      "description": "dummy PT finding for test purposes",
                      "status": FindingStatus.FINISHED,
                      "knowledge_of_target": KnowledgeOfTarget.PUBLIC,
                      "extra_field": "testing extra field which are not part of the model"}

        generic_test_result = {"topic": "test",
                               "type": TestBasicResultType.PASSED,
                               "purpose": "test",
                               "description": "dummy generic test result for test purposes",
                               "request": "extra_field_request",
                               "response": "extra_field_response"}

        pt_finding = PTFinding(**pt_finding)
        pt_finding_dict = pt_finding.model_dump()
        print(f"pt_finding_dict: {pt_finding_dict}")
        pt_finding_clean_dict = self._get_clean_attributes_dict(pt_finding_dict)
        print(f"pt_finding_clean_dict: {pt_finding_clean_dict}")

        generic_test_result = TestResult(**generic_test_result)
        self.platform_api.send_finding(pt_finding)
        self.platform_api.send_finding(generic_test_result)

        return CanTestResult(res_str="success!")

    def teardown(self, exception_type, exception_value, traceback):
        self.logger.info("teardown")


# --- senity checks for runnable usage ---
# generates params schema from the runnable class attributes
print("\nParams schema - private members not included")
print(canRunnableInstance.model_json_schema())


# generate result schema
print("\nResult json schema:")
print(canRunnableInstance.generate_results_schema())

# Initiate runnable - option 1

# with canRunnableInstance(
#     desc="test", cli_args="-as -fsd -dsd"
# ) as runnable_instance:  # noqa
#     result: CanTestResult = runnable_instance()

#     # generates result json object
#     print("\nDirect running results: ")
#     print(result.model_dump_json())


# Initiate runnable - option 2
input = {
    "desc": "test",
    "cli_args": "-as -fsd -dsd",
}

with canRunnableInstance(**input) as runnable_instance:  # noqa
    result: CanTestResult = runnable_instance()

    # generates result json object
    print("\ndictionary running results: ")
    print(result.model_dump_json())
