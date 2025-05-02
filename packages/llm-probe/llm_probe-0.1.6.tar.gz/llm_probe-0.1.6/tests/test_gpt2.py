"""Test case for the GPT2 model probe."""

from typing import Dict

import pytest
import torch

from llm_probe.probe import HFModelProbe


def test_config(gpt2_probe: HFModelProbe) -> None:
    """Test the model configuration."""
    assert gpt2_probe.get_architecture() == "GPT2LMHeadModel"  # noqa: S101
    assert gpt2_probe.get_bos_token_id() == 50256  # noqa: S101
    assert gpt2_probe.get_eos_token_id() == 50256  # noqa: S101
    assert gpt2_probe.get_hidden_act() == "gelu_new"  # noqa: S101
    assert gpt2_probe.get_hidden_size() == 128  # noqa: S101
    assert gpt2_probe.get_max_length() == 1024  # noqa: S101
    assert gpt2_probe.get_num_attention_heads() == 2  # noqa: S101
    assert gpt2_probe.get_num_hidden_layers() == 2  # noqa: S101
    assert gpt2_probe.get_norm_eps() == 1e-05  # noqa: S101
    assert gpt2_probe.get_vocab_size() == 50257  # noqa: S101


def test_input_ids(gpt2_probe: HFModelProbe) -> None:
    """Test the input ids."""
    # Sample prompts with batch size 4
    prompts = [
        "Hello, my name is John.",
        "I am a student in the university.",
        "Good morning, everyone.",
        "The weather is nice today.",
    ]
    # Get input ids with batched ids
    input_ids = gpt2_probe.get_input_ids(prompts, add_special_tokens=False)

    # Check the shape of the input ids
    assert input_ids.shape[0] == 4  # noqa: S101


def test_output_ids(gpt2_probe: HFModelProbe) -> None:
    """Test the output ids."""
    # Forward pass
    input_ids = gpt2_probe.get_input_ids("Hello")
    gpt2_probe.generate(input_ids, max_new_tokens=1)

    # Get output ids
    output_ids = gpt2_probe.get_output_ids(dtype=torch.int16)

    # Check the value of the output ids
    assert output_ids[0, -1].data == 15496  # noqa: S101


@pytest.mark.parametrize(
    "seq_len",
    [
        pytest.param(
            1,
            id="s1",
        ),
        pytest.param(
            16,
            id="s16",
        ),
        pytest.param(
            64,
            id="s64",
        ),
    ],
)
@pytest.mark.parametrize(
    "sub_layer",
    [
        pytest.param(
            {
                "hook": "transformer.wte",
                "input_shape": (1, 1),
                "output_shape": (1, 1, 128),
                "weight_shape": (50257, 128),
                "bias_shape": None,
            },
            id="wte",
        ),
        pytest.param(
            {
                "hook": "transformer.wpe",
                "input_shape": (1, 1),
                "output_shape": (1, 1, 128),
                "weight_shape": (1024, 128),
                "bias_shape": None,
            },
            id="wpe",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.ln_1",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 128),
                "weight_shape": (128,),
                "bias_shape": (128,),
            },
            id="ln_1",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.attn.c_attn",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 384),
                "weight_shape": (128, 384),
                "bias_shape": (384,),
            },
            id="c_attn",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.attn.c_proj",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 128),
                "weight_shape": (128, 128),
                "bias_shape": (128,),
            },
            id="c_proj",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.ln_2",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 128),
                "weight_shape": (128,),
                "bias_shape": (128,),
            },
            id="ln_2",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.mlp.c_fc",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 512),
                "weight_shape": (128, 512),
                "bias_shape": (512,),
            },
            id="c_fc",
        ),
        pytest.param(
            {
                "hook": "transformer.h.0.mlp.c_proj",
                "input_shape": (1, 1, 512),
                "output_shape": (1, 1, 128),
                "weight_shape": (512, 128),
                "bias_shape": (128,),
            },
            id="c_proj",
        ),
        pytest.param(
            {
                "hook": "transformer.ln_f",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 128),
                "weight_shape": (128,),
                "bias_shape": (128,),
            },
            id="ln_f",
        ),
        pytest.param(
            {
                "hook": "lm_head",
                "input_shape": (1, 1, 128),
                "output_shape": (1, 1, 50257),
                "weight_shape": (128, 50257),
                "bias_shape": None,
            },
            id="lm_head",
        ),
    ],
)
def test_layer_probe(gpt2_probe: HFModelProbe, seq_len: int, sub_layer: Dict) -> None:
    """Test the layer probe."""
    # Set module hook
    module = sub_layer["hook"]
    gpt2_probe.set_hook(module)

    # Forward pass
    input_ids = torch.randint(0, gpt2_probe.get_vocab_size(), (1, seq_len))
    gpt2_probe.generate(input_ids, max_new_tokens=1)

    # Check the shape of the module input
    if sub_layer["input_shape"] is not None:
        input_shape = gpt2_probe.get_intermediate_input(module).shape
        answer_shape = list(sub_layer["input_shape"])
        answer_shape[1] = seq_len
        assert input_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module output
    if sub_layer["output_shape"] is not None:
        output_shape = gpt2_probe.get_intermediate_output(module).shape
        answer_shape = list(sub_layer["output_shape"])
        answer_shape[1] = seq_len
        assert output_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module weight
    if sub_layer["weight_shape"] is not None:
        weight_shape = gpt2_probe.get_intermediate_weight(module).shape
        assert weight_shape == sub_layer["weight_shape"]  # noqa: S101

    # Check the shape of the module bias
    if sub_layer["bias_shape"] is not None:
        bias_shape = gpt2_probe.get_intermediate_bias(module).shape
        assert bias_shape == sub_layer["bias_shape"]  # noqa: S101

    # Remove the hook
    gpt2_probe.remove_hooks()
    # Clear the intermediate data
    gpt2_probe.clear_intermediate_data()
