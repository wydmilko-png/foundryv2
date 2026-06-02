"""
providers — pluggable LLM and image backends.

The rest of the pipeline only ever calls:
    get_llm().generate_concepts(brand_data, product_data)
    get_image_generator().generate(concept, refs, out_path)

...so it never knows or cares which model is behind it. Which backend is used is
decided by config (provider:model strings in .env). If the required key is
missing, we transparently fall back to the free local stub.
"""

import config


def get_llm():
    provider, model = config.split_provider(config.LLM_PROVIDER)
    if config.FORCE_STUB or not _llm_key_present(provider):
        from providers import llm_stub
        return llm_stub.StubLLM(reason=_why(provider, config.ANTHROPIC_API_KEY))
    if provider == "anthropic":
        from providers import llm_anthropic
        return llm_anthropic.AnthropicLLM(model)
    raise ValueError(f"Unknown LLM provider: {provider!r} (add an adapter in providers/)")


def get_image_generator():
    provider, model = config.split_provider(config.IMAGE_PROVIDER)
    if config.FORCE_STUB or not _image_key_present(provider):
        from providers import image_stub
        return image_stub.StubImage(reason=_why(provider, config.FAL_KEY))
    if provider == "fal":
        from providers import image_fal
        return image_fal.FalImage(model)
    raise ValueError(f"Unknown image provider: {provider!r} (add an adapter in providers/)")


def _llm_key_present(provider: str) -> bool:
    return provider == "anthropic" and bool(config.ANTHROPIC_API_KEY)


def _image_key_present(provider: str) -> bool:
    return provider == "fal" and bool(config.FAL_KEY)


def _why(provider: str, key: str) -> str:
    if config.FORCE_STUB:
        return "FOUNDRY_STUB is set"
    return f"no API key for provider '{provider}'"
