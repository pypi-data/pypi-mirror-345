from itertools import product

from fi.integrations.otel.fi_types import (
    EvalConfig,
    EvalName,
    EvalSpanKind,
    EvalTag,
    EvalTagType,
)


def get_default_config(eval_name: EvalName):
    # Configs for evals with required fields
    configs = {
        EvalName.DETERMINISTIC_EVALS: {
            "multi_choice": False,
            "choices": ["Yes", "No"],
            "rule_prompt": "Evaluate if the response is correct",
            "input": [],
        },
        EvalName.ENDS_WITH: {"substring": "test", "case_sensitive": True},
        EvalName.EQUALS: {"expected_text": "expected response", "case_sensitive": True},
        EvalName.STARTS_WITH: {"substring": "start", "case_sensitive": True},
        EvalName.CONTAINS: {"keyword": "test", "case_sensitive": True},
        EvalName.AGENT_AS_JUDGE: {
            "eval_prompt": "Judge the response",
            "model": "gpt-4o-mini",
            "system_prompt": "system",
        },
        EvalName.API_CALL: {"url": "https"},
        EvalName.CUSTOM_CODE_EVALUATION: {"code": "for i in abc"},
    }

    # For evals not in the specific configs, return their default configs from EvalConfig
    if eval_name not in configs:
        eval_config = EvalConfig.get_config_for_eval(eval_name)
        return {
            key: field_config["default"] for key, field_config in eval_config.items()
        }

    return configs[eval_name]


eval_tags = [
    EvalTag(
        type=tag_type,
        value=span_kind,
        eval_name=eval_name,
        config=get_default_config(eval_name),
    )
    for tag_type, span_kind, eval_name in product(
        EvalTagType, EvalSpanKind, [EvalName.DETERMINISTIC_EVALS]
    )
]
