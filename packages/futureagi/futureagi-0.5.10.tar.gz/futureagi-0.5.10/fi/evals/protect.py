import copy
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Dict, List, Optional, Tuple

from fi.evals import EvalClient
from fi.evals.templates import (
    DataPrivacyCompliance,
    PromptInjection,
    Sexist,
    Tone,
    Toxicity,
)
from fi.testcases.mllm_test_case import MLLMTestCase


class ProtectClient:
    """Client for protecting against unwanted content using various metrics"""

    def __init__(self, evaluator: EvalClient):
        """
        Initialize ProtectClient

        Args:
            evaluator: Instance of EvalClient to use for evaluations
        """
        self.evaluator = evaluator

        # Map metric names to their corresponding template classes
        self.metric_map = {
            "Toxicity": Toxicity,
            "Tone": Tone,
            "Sexism": Sexist,
            "Prompt Injection": PromptInjection,
            "Data Privacy": DataPrivacyCompliance,
        }
        self.executor = ThreadPoolExecutor(max_workers=5)

    def _check_rule_sync(
        self, rule: Dict, test_case: MLLMTestCase
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Synchronous version of rule checking

        Returns:
            Tuple[str, bool, Optional[str]]: (rule_name, triggered, message if triggered)
        """
        # thread_name = threading.current_thread().name
        # start_time = time.time()
        # print(f"Starting rule check for {rule['metric']} in thread {thread_name} at {start_time}")

        template_class = self.metric_map[rule["metric"]]
        if rule["metric"] == "Data Privacy":
            template = template_class(
                config={"call_type": "protect", "check_internet": False}
            )
            # template = template_class(config={"check_internet": False})
        else:
            template = template_class(config={"call_type": "protect"})
            # template = template_class(config={})

        eval_result = self.evaluator.evaluate(template, test_case)

        # end_time = time.time()
        # print(f"Completed rule check for {rule['metric']} in thread {thread_name} at {end_time} (took {end_time - start_time:.2f}s)")

        reason = ""

        if eval_result.eval_results:
            result = eval_result.eval_results[0]
            detected_values = result.data

            should_trigger = False
            if rule["type"] == "any":
                should_trigger = any(
                    value in rule["contains"] for value in detected_values
                )
            elif rule["type"] == "all":
                should_trigger = all(
                    value in rule["contains"] for value in detected_values
                )

            if should_trigger:
                if rule["reason"]:
                    # message = rule['action'] + f' Reason: {result.reason}'
                    message = rule["action"]
                    reason = result.reason
                else:
                    message = rule["action"]
                return rule["metric"], True, message, reason

        return rule["metric"], False, None, None

    def _process_rules_batch(
        self, rules: List[Dict], test_case: MLLMTestCase, remaining_time: float
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Process a batch of rules in parallel

        Args:
            rules: List of rules to process
            test_case: Test case to evaluate
            remaining_time: Time remaining for processing

        Returns:
            Tuple[List[str], List[str], List[str]]:
                (failure_messages, completed_rules, uncompleted_rules)
        """
        # print(f"\nProcessing batch of {len(rules)} rules")
        # batch_start = time.time()

        # Submit all rules to the thread pool
        future_to_rule = {
            self.executor.submit(self._check_rule_sync, rule, test_case): rule["metric"]
            for rule in rules
        }

        completed_rules = []
        uncompleted_rules = [rule["metric"] for rule in rules]
        failure_messages = []
        failure_reasons = []
        failed_rule = None
        try:
            # Wait for futures to complete with timeout
            for future in as_completed(future_to_rule, timeout=remaining_time):
                rule_name = future_to_rule[future]
                try:
                    metric, triggered, message, reason = future.result()
                    # Update tracking lists
                    completed_rules.append(metric)
                    uncompleted_rules.remove(metric)

                    if triggered:
                        failure_messages.append(message)
                        failure_reasons.append(reason)
                        failed_rule = rule_name
                        # Cancel remaining futures if a rule fails
                        for f in future_to_rule:
                            if not f.done():
                                f.cancel()
                        break

                except Exception as e:
                    print(f"Error processing rule {rule_name}: {e}")

        except TimeoutError:
            print(
                f"Timeout reached. {len(completed_rules)} rules completed, "
                f"{len(uncompleted_rules)} rules incomplete"
            )

        finally:
            # Cancel any remaining futures
            for future in future_to_rule:
                if not future.done():
                    future.cancel()

        # batch_end = time.time()
        # print(f"Batch processing completed in {batch_end - batch_start:.2f}s\n")

        return (
            failure_messages,
            completed_rules,
            uncompleted_rules,
            failure_reasons,
            failed_rule,
        )

    def protect(
        self,
        inputs: str,
        protect_rules: List[Dict],
        action: str = "Response cannot be generated as the input fails the checks",
        reason: bool = False,
        timeout: int = 30000,
    ) -> List[str]:
        """
        Evaluate input strings against protection rules

        Args:
            inputs: Single string or list of strings to evaluate
            protect_rules_copy: List of protection rule dictionaries. Each rule must contain:
                - metric: str, name of the metric to evaluate (e.g., 'Toxicity', 'Tone', 'Sexism')
                - contains: List[str], values to check for in the evaluation results
                - type: str, either 'any' or 'all'
                - action: str, message to return when rule is triggered
                - reason: bool (optional), whether to include the evaluation reason in the message
            timeout: Optional timeout for evaluations

        Returns:
            List of protection messages for failed rules or ["All checks passed"] if no rules are triggered

        Raises:
            ValueError: If inputs or protect_rules_copy don't match the required structure
            TypeError: If inputs contains non-string objects
        """
        timeout = timeout * 1000

        protect_rules_copy = copy.deepcopy(protect_rules)

        # Validate inputs
        if inputs is None:
            raise ValueError("inputs cannot be None")

        if not isinstance(inputs, str):
            raise TypeError(f"inputs must be a string, got {type(inputs)}")

        # Convert single string to list
        if isinstance(inputs, str):
            inputs = [inputs]

        if not inputs:
            raise ValueError("inputs cannot be empty")

        # Validate each input is a non-empty string
        for i, input_text in enumerate(inputs):
            if not isinstance(input_text, str):
                raise TypeError(
                    f"Input at index {i} must be a string, got {type(input_text)}"
                )
            if not input_text.strip():
                raise ValueError(f"Input at index {i} cannot be empty or whitespace")

        # Convert inputs to MLLMTestCase instances with call_type="protect"
        test_cases = [MLLMTestCase(input=input_text, call_type="protect") for input_text in inputs]

        # Validate protect_rules_copy
        if not isinstance(protect_rules_copy, list):
            raise TypeError("protect_rules_copy must be a list")

        if not protect_rules_copy:
            raise ValueError("protect_rules_copy cannot be empty")

        valid_metrics = set(self.metric_map.keys())
        valid_types = {"any", "all"}

        for i, rule in enumerate(protect_rules_copy):

            if not isinstance(rule, dict):
                raise TypeError(f"Rule at index {i} must be a dictionary")

            # Check required keys
            required_keys = {"metric"}
            missing_keys = required_keys - set(rule.keys())
            if missing_keys:
                raise ValueError(
                    f"Rule at index {i} is missing required keys: {missing_keys}"
                )

            if rule["metric"] == "Tone":
                required_keys_tone = {"metric", "contains"}
                missing_keys_tone = required_keys_tone - set(rule.keys())
                if missing_keys_tone:
                    raise ValueError(
                        f"Rule at index {i} is missing required keys: {missing_keys_tone}"
                    )

                # Check for invalid keys
                invalid_keys = set(rule.keys()) - required_keys_tone
                if "type" in rule.keys():
                    invalid_keys -= {"type"}
                if invalid_keys:
                    raise ValueError(
                        f"Invalid key(s) found in rule at index: {invalid_keys}. Valid keys are: {required_keys_tone}"
                    )
            else:
                # required_keys_tone = {'metric'}
                # missing_keys_tone = required_keys_tone - set(rule.keys())
                # if missing_keys_tone:
                #     raise ValueError(f"Rule at index {i} is missing required keys: {missing_keys_tone}")

                # Check for invalid keys
                invalid_keys = set(rule.keys()) - required_keys
                if invalid_keys:
                    raise ValueError(
                        f"Invalid key(s) found in rule at index: {invalid_keys}. Valid keys are: {required_keys}"
                    )

            # required_keys_tone = {'metric', 'contains'}

            # Validate metric
            if rule["metric"] not in valid_metrics:
                raise ValueError(
                    f"Invalid metric '{rule['metric']}' at. "
                    f"Valid metrics are: {list(valid_metrics)}"
                )

            # Validate contains and type only for Tone metric
            if rule["metric"] == "Tone":
                if "contains" not in rule:
                    raise ValueError("'contains' is required for Tone metric")
                if not isinstance(rule["contains"], list):
                    raise TypeError("'contains' in Tone must be a list")
                if not rule["contains"]:
                    raise ValueError("'contains' cannot be empty for Tone metric")

                if "type" not in rule:
                    rule["type"] = "any"
                if rule["type"] not in valid_types:
                    raise ValueError(
                        f"Invalid type '{rule['type']}' at index {i}. "
                        f"Must be one of: {valid_types}"
                    )
            else:
                # For non-Tone metrics, these fields should not be specified
                if "contains" in rule:
                    raise ValueError(
                        f"'contains' should not be specified for {rule['metric']} metric"
                    )
                if "type" in rule:
                    raise ValueError(
                        f"'type' should not be specified for {rule['metric']} metric"
                    )

                # Set default values
                rule["contains"] = ["Failed"]
                rule["type"] = "any"

            # Validate type
            if "type" not in rule:
                rule["type"] = "any"

            if rule["type"] not in valid_types:
                raise ValueError(
                    f"Invalid type '{rule['type']}' at index {i}. "
                    f"Must be one of: {valid_types}"
                )

            # Validate action
            if "action" not in rule:
                rule["action"] = action

            # Set default for reason if not provided
            if "reason" in rule:
                raise ValueError("reason cannot be defined in the rule")
            if "reason" not in rule:
                rule["reason"] = reason

        # results = []
        BATCH_SIZE = 5  # Maximum number of concurrent rule checks
        if len(protect_rules_copy) < BATCH_SIZE:
            BATCH_SIZE = len(protect_rules_copy)

        total_timeout = timeout / 1000  # in seconds
        start_time = time.time()

        all_failure_messages = []
        all_completed_rules = []
        all_uncompleted_rules = []
        all_failure_reasons = []
        # try:
        bool_check_fail = False
        for test_case in test_cases:
            for i in range(0, len(protect_rules_copy), BATCH_SIZE):
                # Calculate remaining time
                elapsed_time = time.time() - start_time
                remaining_time = max(0, total_timeout - elapsed_time)

                if remaining_time <= 0:
                    # Add remaining rules to uncompleted list
                    remaining_rules = [
                        rule["metric"] for rule in protect_rules_copy[i:]
                    ]
                    all_uncompleted_rules.extend(remaining_rules)
                    break

                rules_batch = protect_rules_copy[i : i + BATCH_SIZE]
                (
                    messages,
                    completed,
                    uncompleted,
                    failure_reasons,
                    failed_rule,
                ) = self._process_rules_batch(rules_batch, test_case, remaining_time)

                all_completed_rules.extend(completed)
                all_uncompleted_rules.extend(uncompleted)
                all_failure_reasons.extend(failure_reasons)
                if messages:
                    all_failure_messages.extend(messages)
                    bool_check_fail = True
                    break

        ans = {
            "status": "failed" if all_failure_messages else "passed",
            "completed_rules": all_completed_rules,
            "uncompleted_rules": all_uncompleted_rules,
            "failed_rule": failed_rule,
            "messages": (
                all_failure_messages[0] if all_failure_messages else "All checks passed"
            ),
            "reasons": (
                all_failure_reasons[0] if all_failure_reasons else "All checks passed"
            ),
            "time_taken": elapsed_time,
        }

        if len(ans["uncompleted_rules"]) == len(protect_rules_copy):
            ans["reason"] = "No checks completed"

        if bool_check_fail:
            ans["status"] = "failed"
        else:
            ans["status"] = "passed"
            # ans['messages'] = inputs

        if ans["status"] == "passed":
            ans["messages"] = inputs[0]

        return ans
