"""Test the rotary embedding module."""

from transformers import AutoConfig

from llm_probe.probe.plugin.rotary_embedding import RotaryEmbedding


def test_rotary_embedding():
    """Test the rotary embedding module."""
    # Load the model configuration
    config = AutoConfig.from_pretrained("hyper-accel/tiny-random-llama")
    hidden_size = config.hidden_size
    num_attention_heads = config.num_attention_heads
    max_length = config.max_position_embeddings

    # Initialize the rotary embedding
    rotary_emb = RotaryEmbedding(config)

    # Get the rotary embedding
    cos, sin = rotary_emb.get_rotary_embedding(max_length=max_length)

    # Check the shape of the rotary embedding
    rotary_dim = hidden_size // num_attention_heads
    assert cos.shape == (max_length, rotary_dim)
    assert sin.shape == (max_length, rotary_dim)
