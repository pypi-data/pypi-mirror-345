"""Test fixture for model probe."""

import logging
from typing import Tuple

import pytest
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer

# LLM probe python package
from llm_probe.probe import HFModelProbe

# Huggingface Moel ID
GPT2_MODEL_ID = "hyper-accel/tiny-random-gpt2"
LLAMA_MODEL_ID = "hyper-accel/tiny-random-llama"
MIXTAL_MODEL_ID = "TitanML/tiny-mixtral"

# Logger
logger = logging.getLogger(__name__)


def download_model(model_id: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Download the model and tokenizer. If gated, ask for login and retry."""
    try:
        model = AutoModelForCausalLM.from_pretrained(model_id)
        tokenizer = AutoTokenizer.from_pretrained(model_id, clean_up_tokenization_spaces=True)
        return model, tokenizer
    except Exception as e:
        logger.warning(f"Initial download failed: {e}")
        logger.warning("This model may require authentication (gated model).")

        # Try login
        try:
            token = input("Enter your Hugging Face token: ").strip()
            login(token=token)
            logger.info("Logged in successfully. Retrying...")

            # Try again
            model = AutoModelForCausalLM.from_pretrained(model_id, token=token)
            tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
            return model, tokenizer
        except Exception as login_error:
            err_msg = f"Login failed or retry failed: {login_error}"
            raise RuntimeError(err_msg) from login_error


@pytest.fixture(scope="session")
def gpt2_probe() -> HFModelProbe:
    """Test fixture for gpt2 model."""
    model, tokenizer = download_model(GPT2_MODEL_ID)
    return HFModelProbe(model, tokenizer)


@pytest.fixture(scope="session")
def llama_probe() -> HFModelProbe:
    """Test fixture for llama model."""
    model, tokenizer = download_model(LLAMA_MODEL_ID)
    return HFModelProbe(model, tokenizer)


@pytest.fixture(scope="session")
def mixtral_probe() -> HFModelProbe:
    """Test fixture for mixtral model."""
    model, tokenizer = download_model(MIXTAL_MODEL_ID)
    return HFModelProbe(model, tokenizer)


@pytest.fixture(scope="session")
def moe_model() -> AutoModelForCausalLM:
    """Test fixture for TinyMixtral model."""
    model = AutoModelForCausalLM.from_pretrained(MIXTAL_MODEL_ID)
    return model
