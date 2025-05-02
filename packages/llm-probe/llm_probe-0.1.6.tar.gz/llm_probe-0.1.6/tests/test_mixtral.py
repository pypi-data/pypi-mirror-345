"""Test case for the Mixtral model probe."""

from typing import Dict

import pytest
import torch

from llm_probe.probe import HFModelProbe


def test_config(mixtral_probe: HFModelProbe) -> None:
    """Test the model configuration."""
    assert mixtral_probe.get_architecture() == "MixtralForCausalLM"  # noqa: S101
    assert mixtral_probe.get_bos_token_id() == 1  # noqa: S101
    assert mixtral_probe.get_eos_token_id() == 2  # noqa: S101
    assert mixtral_probe.get_hidden_act() == "silu"  # noqa: S101
    assert mixtral_probe.get_hidden_size() == 1024  # noqa: S101
    assert mixtral_probe.get_intermediate_size() == 3584  # noqa: S101
    assert mixtral_probe.get_max_length() == 131072  # noqa: S101
    assert mixtral_probe.get_num_attention_heads() == 32  # noqa: S101
    assert mixtral_probe.get_num_key_value_heads() == 8  # noqa: S101
    assert mixtral_probe.get_num_hidden_layers() == 2  # noqa: S101
    assert mixtral_probe.get_norm_eps() == 1e-05  # noqa: S101
    assert mixtral_probe.get_vocab_size() == 32000  # noqa: S101
    assert mixtral_probe.get_num_experts_per_tok() == 2  # noqa: S101
    assert mixtral_probe.get_num_local_experts() == 8  # noqa: S101


def test_input_ids(mixtral_probe: HFModelProbe) -> None:
    """Test the input ids."""
    # Sample prompts with batch size 4
    prompts = [
        "Hello, my name is John.",
        "I am a student in the university.",
        "Good morning, everyone.",
        "The weather is nice today.",
    ]
    # Get input ids with batched ids
    input_ids = mixtral_probe.get_input_ids(prompts, add_special_tokens=False)

    # Check the shape of the input ids
    assert input_ids.shape[0] == 4  # noqa: S101


def test_output_ids(mixtral_probe: HFModelProbe) -> None:
    """Test the output ids."""
    # Forward pass
    input_ids = mixtral_probe.get_input_ids("Hello")
    mixtral_probe.generate(input_ids, max_new_tokens=1)

    # Get output ids
    output_ids = mixtral_probe.get_output_ids(dtype=torch.int16)

    # Check the value of the output ids
    assert output_ids[0, -1].data == 295  # noqa: S101


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
                "hook": "model.embed_tokens",
                "input_shape": (1, 2),
                "output_shape": (1, 2, 1024),
                "weight_shape": (32000, 1024),
                "bias_shape": None,
            },
            id="embed_tokens",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.input_layernorm",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 1024),
                "weight_shape": (1024,),
                "bias_shape": None,
            },
            id="input_layernorm",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.q_proj",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 1024),
                "weight_shape": (1024, 1024),
                "bias_shape": None,
            },
            id="q_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.k_proj",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 256),
                "weight_shape": (1024, 256),
                "bias_shape": None,
            },
            id="k_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.v_proj",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 256),
                "weight_shape": (1024, 256),
                "bias_shape": None,
            },
            id="v_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.o_proj",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 1024),
                "weight_shape": (1024, 1024),
                "bias_shape": None,
            },
            id="o_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.post_attention_layernorm",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 1024),
                "weight_shape": (1024,),
                "bias_shape": None,
            },
            id="post_attention_layernorm",
        ),
        pytest.param(
            {
                "hook": "model.norm",
                "input_shape": (1, 2, 1024),
                "output_shape": (1, 2, 1024),
                "weight_shape": (1024,),
                "bias_shape": None,
            },
            id="norm",
        ),
    ],
)
def test_layer_probe(mixtral_probe: HFModelProbe, seq_len: int, sub_layer: Dict) -> None:
    """Test the layer probe."""
    # Set module hook
    module = sub_layer["hook"]
    mixtral_probe.set_hook(module)

    # Forward pass
    input_ids = torch.randint(0, mixtral_probe.get_vocab_size(), (1, seq_len))
    mixtral_probe.generate(input_ids, max_new_tokens=1)

    # Check the shape of the module input
    if sub_layer["input_shape"] is not None:
        input_shape = mixtral_probe.get_intermediate_input(module).shape
        answer_shape = list(sub_layer["input_shape"])
        answer_shape[1] = seq_len
        assert input_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module output
    if sub_layer["output_shape"] is not None:
        output_shape = mixtral_probe.get_intermediate_output(module).shape
        answer_shape = list(sub_layer["output_shape"])
        answer_shape[1] = seq_len
        assert output_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module weight
    if sub_layer["weight_shape"] is not None:
        weight_shape = mixtral_probe.get_intermediate_weight(module).shape
        assert weight_shape == sub_layer["weight_shape"]  # noqa: S101

    # Check the shape of the module bias
    if sub_layer["bias_shape"] is not None:
        bias_shape = mixtral_probe.get_intermediate_bias(module).shape
        assert bias_shape == sub_layer["bias_shape"]  # noqa: S101

    # Remove the hook
    mixtral_probe.remove_hooks()
    # Clear the intermediate data
    mixtral_probe.clear_intermediate_data()


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
                "hook": "model.layers.0.block_sparse_moe.experts.0.w1",
                "input_shape": (2, 2, 1024),
                "output_shape": (2, 2, 3584),
                "weight_shape": (1024, 3584),
                "bias_shape": None,
            },
            id="moe_w1",
        ),
        pytest.param(
            {
                "hook": "model.layers.1.block_sparse_moe.experts.0.w2",
                "input_shape": (2, 2, 3584),
                "output_shape": (2, 2, 1024),
                "weight_shape": (3584, 1024),
                "bias_shape": None,
            },
            id="moe_w2",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.block_sparse_moe.experts.0.w3",
                "input_shape": (2, 2, 1024),
                "output_shape": (2, 2, 3584),
                "weight_shape": (1024, 3584),
                "bias_shape": None,
            },
            id="moe_w3",
        ),
    ],
)
def test_moe_probe(mixtral_probe: HFModelProbe, seq_len: int, sub_layer: Dict) -> None:
    """Test the moe probe."""
    # Set module hook
    module = sub_layer["hook"]
    mixtral_probe.set_hook(module)

    # Forward pass
    input_ids = torch.randint(0, mixtral_probe.get_vocab_size(), (1, seq_len))
    mixtral_probe.generate(input_ids, max_new_tokens=1)

    # Check the shape of the module input
    if sub_layer["input_shape"] is not None:
        input_shape = mixtral_probe.get_intermediate_input(module).shape
        answer_shape = list(sub_layer["input_shape"])
        answer_shape[0] = seq_len
        assert input_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module output
    if sub_layer["output_shape"] is not None:
        output_shape = mixtral_probe.get_intermediate_output(module).shape
        answer_shape = list(sub_layer["output_shape"])
        answer_shape[0] = seq_len
        assert output_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module weight
    if sub_layer["weight_shape"] is not None:
        weight_shape = mixtral_probe.get_intermediate_weight(module).shape
        assert weight_shape == sub_layer["weight_shape"]  # noqa: S101

    # Check the shape of the module bias
    if sub_layer["bias_shape"] is not None:
        bias_shape = mixtral_probe.get_intermediate_bias(module).shape
        assert bias_shape == sub_layer["bias_shape"]  # noqa: S101

    # Remove the hook
    mixtral_probe.remove_hooks()
    # Clear the intermediate data
    mixtral_probe.clear_intermediate_data()


def test_rotary_embedding(mixtral_probe: HFModelProbe) -> None:
    """Test the rotary embedding."""
    # Get the rotary embedding
    cos, sin = mixtral_probe.get_rotary_embedding()

    # Check the shape of the rotary embedding
    max_length = mixtral_probe.get_max_length()
    head_dim = mixtral_probe.get_hidden_size() // mixtral_probe.get_num_attention_heads()
    assert cos.shape == (max_length, head_dim)  # noqa: S101
    assert sin.shape == (max_length, head_dim)  # noqa: S101
