"""Test case for the Llama model probe."""

from typing import Dict

import pytest
import torch

from llm_probe.probe import HFModelProbe


def test_config(llama_probe: HFModelProbe) -> None:
    """Test the model configuration."""
    assert llama_probe.get_architecture() == "LlamaForCausalLM"  # noqa: S101
    assert llama_probe.get_bos_token_id() == 128000  # noqa: S101
    assert llama_probe.get_eos_token_id() == 128001  # noqa: S101
    assert llama_probe.get_hidden_act() == "silu"  # noqa: S101
    assert llama_probe.get_hidden_size() == 512  # noqa: S101
    assert llama_probe.get_intermediate_size() == 2048  # noqa: S101
    assert llama_probe.get_max_length() == 131072  # noqa: S101
    assert llama_probe.get_num_attention_heads() == 8  # noqa: S101
    assert llama_probe.get_num_key_value_heads() == 2  # noqa: S101
    assert llama_probe.get_num_hidden_layers() == 2  # noqa: S101
    assert llama_probe.get_norm_eps() == 1e-05  # noqa: S101
    assert llama_probe.get_vocab_size() == 128256  # noqa: S101


def test_input_ids(llama_probe: HFModelProbe) -> None:
    """Test the input ids."""
    # Sample prompts with batch size 4
    prompts = [
        "Hello, my name is John.",
        "I am a student in the university.",
        "Good morning, everyone.",
        "The weather is nice today.",
    ]
    # Get input ids with batched ids
    input_ids = llama_probe.get_input_ids(prompts, add_special_tokens=False)

    # Check the shape of the input ids
    assert input_ids.shape[0] == 4  # noqa: S101


def test_output_ids(llama_probe: HFModelProbe) -> None:
    """Test the output ids."""
    # Forward pass
    input_ids = llama_probe.get_input_ids("Hello")
    llama_probe.generate(input_ids, max_new_tokens=1)

    # Get output ids
    output_ids = llama_probe.get_output_ids(dtype=torch.int16)

    # Check the value of the output ids
    assert output_ids[0, -1].data == 4903  # noqa: S101


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
                "output_shape": (1, 2, 512),
                "weight_shape": (128256, 512),
                "bias_shape": None,
            },
            id="embed_tokens",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.input_layernorm",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 512),
                "weight_shape": (512,),
                "bias_shape": None,
            },
            id="input_layernorm",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.q_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 512),
                "weight_shape": (512, 512),
                "bias_shape": None,
            },
            id="q_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.k_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 128),
                "weight_shape": (512, 128),
                "bias_shape": None,
            },
            id="k_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.v_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 128),
                "weight_shape": (512, 128),
                "bias_shape": None,
            },
            id="v_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.self_attn.o_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 512),
                "weight_shape": (512, 512),
                "bias_shape": None,
            },
            id="o_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.post_attention_layernorm",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 512),
                "weight_shape": (512,),
                "bias_shape": None,
            },
            id="post_attention_layernorm",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.mlp.up_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 2048),
                "weight_shape": (512, 2048),
                "bias_shape": None,
            },
            id="up_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.mlp.gate_proj",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 2048),
                "weight_shape": (512, 2048),
                "bias_shape": None,
            },
            id="gate_proj",
        ),
        pytest.param(
            {
                "hook": "model.layers.0.mlp.down_proj",
                "input_shape": (1, 2, 2048),
                "output_shape": (1, 2, 512),
                "weight_shape": (2048, 512),
                "bias_shape": None,
            },
            id="down_proj",
        ),
        pytest.param(
            {
                "hook": "model.norm",
                "input_shape": (1, 2, 512),
                "output_shape": (1, 2, 512),
                "weight_shape": (512,),
                "bias_shape": None,
            },
            id="norm",
        ),
    ],
)
def test_layer_probe(llama_probe: HFModelProbe, seq_len: int, sub_layer: Dict) -> None:
    """Test the layer probe."""
    # Set module hook
    module = sub_layer["hook"]
    llama_probe.set_hook(module)

    # Forward pass
    input_ids = torch.randint(0, llama_probe.get_vocab_size(), (1, seq_len))
    llama_probe.generate(input_ids, max_new_tokens=1)

    # Check the shape of the module input
    if sub_layer["input_shape"] is not None:
        input_shape = llama_probe.get_intermediate_input(module).shape
        answer_shape = list(sub_layer["input_shape"])
        answer_shape[1] = seq_len
        assert input_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module output
    if sub_layer["output_shape"] is not None:
        output_shape = llama_probe.get_intermediate_output(module).shape
        answer_shape = list(sub_layer["output_shape"])
        answer_shape[1] = seq_len
        assert output_shape == tuple(answer_shape)  # noqa: S101

    # Check the shape of the module weight
    if sub_layer["weight_shape"] is not None:
        weight_shape = llama_probe.get_intermediate_weight(module).shape
        assert weight_shape == sub_layer["weight_shape"]  # noqa: S101

    # Check the shape of the module bias
    if sub_layer["bias_shape"] is not None:
        bias_shape = llama_probe.get_intermediate_bias(module).shape
        assert bias_shape == sub_layer["bias_shape"]  # noqa: S101

    # Remove the hook
    llama_probe.remove_hooks()
    # Clear the intermediate data
    llama_probe.clear_intermediate_data()


def test_rotary_embedding(llama_probe: HFModelProbe) -> None:
    """Test the rotary embedding."""
    # Get the rotary embedding
    cos, sin = llama_probe.get_rotary_embedding()

    # Check the shape of the rotary embedding
    max_length = llama_probe.get_max_length()
    head_dim = llama_probe.get_hidden_size() // llama_probe.get_num_attention_heads()
    assert cos.shape == (max_length, head_dim)  # noqa: S101
    assert sin.shape == (max_length, head_dim)  # noqa: S101
