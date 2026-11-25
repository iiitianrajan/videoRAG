"""Shared LiteLLM routing for every text-generation feature."""

from __future__ import annotations

from functools import lru_cache
import logging
import os
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
import litellm
from litellm import Router


LOGGER = logging.getLogger(__name__)

# Providers do not all implement the same optional controls. For example,
# Gemini 3.8 Flash rejects `temperature`; LiteLLM should omit unsupported
# options on that fallback instead of failing the entire request.
litellm.drop_params = True

PROVIDERS = (
    ("groq", "GROQ_MODEL", "groq/openai/gpt-oss-120b", ("GROQ_API_KEY",)),
    (
        "gemini",
        "GEMINI_MODEL",
        "gemini/gemini-3.8-flash",
        ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    ),
    ("mistral", "MISTRAL_MODEL", "mistral/mistral-small-latest", ("MISTRAL_API_KEY",)),
)


def _configured_deployments() -> list[dict[str, Any]]:
    deployments = []
    for name, model_variable, default_model, key_variables in PROVIDERS:
        api_key = next((os.getenv(variable) for variable in key_variables if os.getenv(variable)), None)
        if api_key:
            deployments.append(
                {
                    "model_name": name,
                    "litellm_params": {
                        "model": os.getenv(model_variable, default_model),
                        "api_key": api_key,
                    },
                }
            )
        else:
            LOGGER.warning(
                "%s is unavailable to the fallback router: set one of %s.",
                name,
                " or ".join(key_variables),
            )
    if not deployments:
        raise RuntimeError(
            "No LLM API key is configured. Set GROQ_API_KEY, GEMINI_API_KEY, or MISTRAL_API_KEY."
        )
    return deployments


@lru_cache(maxsize=1)
def _router() -> tuple[Router, str]:
    deployments = _configured_deployments()
    configured_names = [deployment["model_name"] for deployment in deployments]
    fallbacks = [
        {configured_names[index]: configured_names[index + 1 :]}
        for index in range(len(configured_names) - 1)
    ]
    if configured_names[0] != "groq":
        LOGGER.warning("GROQ_API_KEY is not configured; starting LLM routing with %s.", configured_names[0])

    return (
        Router(
            model_list=deployments,
            fallbacks=fallbacks,
            num_retries=1,
            allowed_fails=1,
            cooldown_time=30,
        ),
        configured_names[0],
    )


def _as_litellm_messages(prompt: Any) -> list[dict[str, str]]:
    messages = prompt.to_messages() if hasattr(prompt, "to_messages") else prompt
    role_map = {"human": "user", "ai": "assistant", "system": "system", "tool": "tool"}
    return [
        {
            "role": role_map.get(message.type, message.type),
            "content": str(message.content),
        }
        for message in messages
    ]


def get_llm(temperature: float = 0.3) -> RunnableLambda:
    """Return a LangChain-compatible runnable backed by LiteLLM's Router."""
    router, primary_model = _router()

    def complete(prompt: Any) -> AIMessage:
        response = router.completion(
            model=primary_model,
            messages=_as_litellm_messages(prompt),
            temperature=temperature,
        )
        return AIMessage(content=response.choices[0].message.content or "")

    return RunnableLambda(complete)
