"""Test case for the utils."""

from transformers import AutoModelForCausalLM

from llm_probe.utils import get_all_module_list


def test_get_all_module_list() -> None:
    """Test the get all module list."""
    # Load the model
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    # Get all module list
    module_list = get_all_module_list(model)
    # Check the length of the module list
    assert len(module_list) == 164  # noqa: S101
