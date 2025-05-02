"""Test the block sparse MoE module."""

import pytest
import torch
from transformers import AutoModelForCausalLM

from llm_probe.models import get_hf_config
from llm_probe.probe.plugin.block_sparse_moe import BlockSparseMoE


def test_moe_layer_pattern(moe_model: AutoModelForCausalLM):
    """Test the block sparse MoE module."""
    # Initialize the block sparse MoE
    block_sparse_moe = BlockSparseMoE(moe_model)

    # Check the gate layer of block sparse MoE
    gate_layer = "model.layers.0.block_sparse_moe.gate"
    assert block_sparse_moe.is_moe_block(gate_layer)

    # Check the weight matrix layer of block sparse MoE
    w1_layer = "model.layers.0.block_sparse_moe.experts.0.w1"
    assert block_sparse_moe.is_moe_block(w1_layer)

    # Check the weight matrix layer of block sparse MoE
    w2_layer = "model.layers.0.block_sparse_moe.experts.0.w2"
    assert block_sparse_moe.is_moe_block(w2_layer)

    # Check the weight matrix layer of block sparse MoE
    w3_layer = "model.layers.0.block_sparse_moe.experts.0.w3"
    assert block_sparse_moe.is_moe_block(w3_layer)


def test_extract_layer_idx(moe_model: AutoModelForCausalLM):
    """Test the extract_layer_idx method."""
    # Initialize the block sparse MoE
    block_sparse_moe = BlockSparseMoE(moe_model)

    # Test wrong layer
    wrong_layer = "model.embed_tokens"
    with pytest.raises(ValueError):
        block_sparse_moe.extract_layer_idx(wrong_layer)

    # Test the gate layer
    gate_layer = "model.layers.0.block_sparse_moe.gate"
    assert block_sparse_moe.extract_layer_idx(gate_layer) == 0

    # Test the weight matrix layer
    w1_layer = "model.layers.4.block_sparse_moe.experts.0.w1"
    assert block_sparse_moe.extract_layer_idx(w1_layer) == 4

    # Test the weight matrix layer
    w2_layer = "model.layers.8.block_sparse_moe.experts.0.w2"
    assert block_sparse_moe.extract_layer_idx(w2_layer) == 8

    # Test the weight matrix layer
    w3_layer = "model.layers.12.block_sparse_moe.experts.0.w3"
    assert block_sparse_moe.extract_layer_idx(w3_layer) == 12


def test_extract_expert_idx(moe_model: AutoModelForCausalLM):
    """Test the extract_expert_idx method."""
    # Initialize the block sparse MoE
    block_sparse_moe = BlockSparseMoE(moe_model)

    # Test wrong layer
    wrong_layer = "model.layers.0.block_sparse_moe.gate"
    with pytest.raises(ValueError):
        block_sparse_moe.extract_expert_idx(wrong_layer)

    # Test the weight matrix layer
    w1_layer = "model.layers.4.block_sparse_moe.experts.0.w1"
    assert block_sparse_moe.extract_expert_idx(w1_layer) == 0

    # Test the weight matrix layer
    w2_layer = "model.layers.8.block_sparse_moe.experts.1.w2"
    assert block_sparse_moe.extract_expert_idx(w2_layer) == 1

    # Test the weight matrix layer
    w3_layer = "model.layers.12.block_sparse_moe.experts.2.w3"
    assert block_sparse_moe.extract_expert_idx(w3_layer) == 2


def test_get_expert_ids(moe_model: AutoModelForCausalLM):
    """Test the get_expert_ids method."""
    # Initialize the block sparse MoE
    block_sparse_moe = BlockSparseMoE(moe_model)
    num_local_experts = get_hf_config(moe_model, "num_local_experts")
    num_experts_per_tok = get_hf_config(moe_model, "num_experts_per_tok")

    # Set wrong gate output dimension
    gate_output = torch.randn(1, 8, 8)
    with pytest.raises(ValueError):
        block_sparse_moe.get_expert_ids(gate_output)

    # Set the descending order of gate output
    gate_output = torch.randn(8, num_local_experts)
    gate_output = torch.sort(gate_output, descending=True, dim=1)[0]

    # Get the expert IDs
    expert_ids = block_sparse_moe.get_expert_ids(gate_output)
    expected_expert_ids = torch.arange(num_experts_per_tok).repeat(8, 1)
    assert torch.all(expert_ids == expected_expert_ids)

    # Set the ascending order of gate output
    gate_output = torch.sort(gate_output, descending=False, dim=1)[0]

    # Get the expert IDs
    expert_ids = block_sparse_moe.get_expert_ids(gate_output)
    expected_expert_ids = torch.arange(num_local_experts - num_experts_per_tok, num_local_experts).flip(0).repeat(8, 1)
    assert torch.all(expert_ids == expected_expert_ids)


def test_get_expert_tensor(moe_model: AutoModelForCausalLM):
    """Test the get_expert_tensor method."""
    # Initialize the block sparse MoE
    block_sparse_moe = BlockSparseMoE(moe_model)
    num_local_experts = get_hf_config(moe_model, "num_local_experts")
    num_experts_per_tok = get_hf_config(moe_model, "num_experts_per_tok")
    hidden_size = get_hf_config(moe_model, "hidden_size")
    seq_len = 8

    # Set the descending order of gate output
    gate_output = torch.randn(seq_len, num_local_experts)
    gate_output = torch.sort(gate_output, descending=True, dim=1)[0]

    # Set the moe output
    active_moe_output = [torch.randn(seq_len, hidden_size) for _ in range(num_experts_per_tok)]
    inactive_moe_output = [torch.randn(0, hidden_size) for _ in range(num_local_experts - num_experts_per_tok)]
    moe_output = active_moe_output + inactive_moe_output

    # Get the expert output
    expert_output = block_sparse_moe.get_expert_tensor(gate_output, moe_output)
    assert expert_output.shape == (seq_len, num_experts_per_tok, hidden_size)
