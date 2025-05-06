import hashlib
from typing import Any

from baml_agents._baml_client_proxy._hooks._implementations._test_generator_helpers import (
    get_args_block_str,
)
from baml_agents._baml_client_proxy._hooks._on_before_call_hook import (
    OnBeforeCallHookContext,
    OnBeforeCallHookSync,
)


def generate_baml_test(test_name, baml_function_name, params):
    return f"""\
test {test_name} {{
  functions [{baml_function_name}]
  args {{
{get_args_block_str(params)}
  }}
}}\n\n"""


def get_test_name(params, baml_function_name):
    hash_input = f"{baml_function_name}{params}"
    return f"t_{hashlib.md5(hash_input.encode()).hexdigest()[:6]}"  # noqa: S324


class BamlTestGeneratorHook(OnBeforeCallHookSync):
    def __init__(self):
        self.baml_test_source_code = ""

    def on_before_call(self, params: dict[str, Any], ctx: OnBeforeCallHookContext):
        test_name = get_test_name(params, ctx.baml_function_name)
        self.baml_test_source_code += generate_baml_test(
            test_name, ctx.baml_function_name, params
        )
