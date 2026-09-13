"""Thin wrapper around HF Inference API / local transformers pipeline."""

import os
from huggingface_hub import InferenceClient


def query_hf_inference(model_id: str, question: str, token: str | None = None) -> str:
    """Query a model via the Hugging Face Inference API."""
    token = token or os.environ.get("HF_TOKEN")
    client = InferenceClient(model=model_id, token=token)
    prompt = (
        f"Answer the following question in one short phrase, "
        f"with no explanation.\nQuestion: {question}\nAnswer:"
    )
    response = client.text_generation(prompt, max_new_tokens=30)
    return response.strip()


def query_local_model(model_id: str, question: str) -> str:
    """Query a model loaded locally via transformers (requires the
    'local-models' extra: pip install f1-temporal-bench[local-models])."""
    from transformers import pipeline

    generator = pipeline("text-generation", model=model_id)
    prompt = (
        f"Answer the following question in one short phrase, "
        f"with no explanation.\nQuestion: {question}\nAnswer:"
    )
    result = generator(prompt, max_new_tokens=30, do_sample=False)
    return result[0]["generated_text"][len(prompt):].strip()