#!/usr/bin/env python3
"""Fetch and update OpenRouter models from their live API.

This script:
1. Queries OpenRouter's /models endpoint to get all available models
2. Filters for high-quality models from open-source and research providers
3. Excludes models available via native APIs (OpenAI, Google, Anthropic, X.AI)
4. Extracts capabilities from the API response
5. Estimates intelligence scores based on model metadata
6. Merges with curated aliases and scores from an existing config
7. Generates an updated conf/openrouter_models.json

Provider Strategy:
- EXCLUDED: OpenAI, Google, Anthropic, X.AI, Perplexity (use native APIs instead)
- INCLUDED: Mistral, Llama, DeepSeek, Qwen, and specialized/research providers

Intelligence Scoring:
- Automatically calculated based on: context window, reasoning capability, recency, tier
- Can be overridden manually by editing the config file
- Score range: 1-20 (5=base, 10=standard, 15+=advanced)

Usage:
    python scripts/sync_openrouter_models.py [--output PATH] [--keep-aliases]

Options:
    --output PATH           Path to output config file (default: conf/openrouter_models.json)
    --keep-aliases          Preserve aliases from existing config (preserves custom scores too)
"""

import argparse
import json
import logging
import os
import sys
import urllib.request

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_openrouter_models(api_key: str | None = None) -> dict:
    """Fetch all available models from OpenRouter's API.

    Args:
        api_key: Optional OpenRouter API key for authenticated requests

    Returns:
        dict mapping model_name -> model_info from OpenRouter API
    """
    url = "https://openrouter.ai/api/v1/models"

    logger.info(f"Fetching models from {url}...")

    try:
        request = urllib.request.Request(url)
        if api_key:
            request.add_header("Authorization", f"Bearer {api_key}")

        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        models = {}
        if "data" in data:
            for model in data["data"]:
                model_id = model.get("id")
                if model_id:
                    models[model_id] = model
                    logger.debug(f"Found model: {model_id}")

        logger.info(f"Successfully fetched {len(models)} models from OpenRouter")
        return models

    except Exception as e:
        logger.error(f"Failed to fetch models from OpenRouter: {e}")
        raise


def estimate_intelligence_score(api_model: dict) -> int:
    """Estimate intelligence score based on OpenRouter metadata.

    Uses model characteristics (context size, reasoning capability, recency, specialization) to
    estimate capability level 1-20. This is a heuristic since OpenRouter doesn't
    provide official rankings.

    Args:
        api_model: Model dict from OpenRouter API

    Returns:
        Estimated intelligence score 1-20
    """
    score = 5  # Base score

    model_id = api_model.get("id", "").lower()
    name = api_model.get("name", "").lower()
    created = api_model.get("created", 0)

    # Reward recent models (created in last 6 months)
    import time

    six_months_ago = time.time() - (6 * 30 * 24 * 3600)
    if created > six_months_ago:
        score += 2

    # Context window indicators
    context = api_model.get("context_length", 32768)
    if context >= 1000000:  # 1M+ context (frontier)
        score += 4
    elif context >= 256000:  # 256K+ context
        score += 3
    elif context >= 200000:  # 200K+ context
        score += 2
    elif context >= 100000:  # 100K+ context
        score += 1

    # Reasoning/thinking capability
    if any(term in name for term in ["reasoning", "r1", "deep-research", "deep-think"]):
        score += 3
    elif any(term in name for term in ["thinking", "pro"]):
        score += 2

    # Specialized high-capability models - these are frontier specialists
    # These are your requested top models - boost them significantly
    if "grok" in model_id and ("grok-4" in model_id or "grok-code" in model_id):
        score += 4  # xAI Grok 4 or Grok Code
    elif "minimax" in model_id:
        score += 4  # MiniMax frontier
    elif "qwen3-coder" in model_id or ("qwen" in model_id and "coder" in name):
        score += 4  # Qwen3 code specialist
    elif "glm" in model_id and ("glm-4.6" in model_id or "glm 4.6" in name):
        score += 4  # GLM 4.6 latest
    elif "grok-3" in model_id or "grok 3" in name:
        score += 2
    elif "qwen3" in model_id or "qwen3" in name:
        score += 2
    elif ("glm-4" in model_id or "glm 4" in name) and "4.5" not in model_id and "4.5" not in name:
        score += 1
    elif "glm-4.5" in model_id or "glm 4.5" in name:
        score += 2
    elif "jamba" in name and ("large" in name or "premier" in name):
        score += 2

    # Model series/tier indicators
    if any(term in name for term in ["70b", "405b", "480b", "1.7", "large", "max"]):
        score += 2
    elif any(term in name for term in ["mini", "small", "lite", "3b", "8b"]):
        score -= 1

    # Vision/multimodal capability
    architecture = api_model.get("architecture", {})
    if "vision" in str(architecture).lower() or "image" in api_model.get("supported_parameters", []):
        score += 1

    # Clamp to 1-20 range
    return max(1, min(20, score))


def extract_model_capabilities(api_model: dict) -> dict:
    """Extract model capabilities from OpenRouter API response.

    Args:
        api_model: Model dict from OpenRouter API

    Returns:
        Dict with capability fields for our config format
    """
    capabilities = {
        "model_name": api_model.get("id", ""),
        "aliases": [],
        "context_window": api_model.get("context_length", 32768),
        "max_output_tokens": api_model.get("max_completion_tokens", 32768),
        "supports_json_mode": True,  # Most OpenRouter models support JSON
        "supports_function_calling": True,  # Most OpenRouter models support functions
        "supports_extended_thinking": False,  # Default to false unless specified
        "supports_images": "vision" in api_model.get("architecture", {}).get("modality", "").lower()
        or "multimodal" in api_model.get("name", "").lower(),
        "max_image_size_mb": 20.0 if "vision" in str(api_model).lower() else 0.0,
        "supports_temperature": True,  # Most models support temperature
        "description": api_model.get("description", ""),
        "intelligence_score": estimate_intelligence_score(api_model),
    }

    # Handle thinking/reasoning capability
    if "reasoning" in api_model.get("name", "").lower() or "r1" in api_model.get("id", "").lower():
        capabilities["supports_extended_thinking"] = True

    return {k: v for k, v in capabilities.items() if v is not None}


def load_existing_config(config_path: str) -> dict:
    """Load existing config to preserve curated data.

    Args:
        config_path: Path to existing openrouter_models.json

    Returns:
        Dict with existing README and models indexed by model_name
    """
    if not os.path.exists(config_path):
        return {"_README": {}, "models_by_name": {}}

    try:
        with open(config_path) as f:
            config = json.load(f)

        models_by_name = {}
        for model in config.get("models", []):
            models_by_name[model.get("model_name")] = model

        return {
            "_README": config.get("_README", {}),
            "models_by_name": models_by_name,
        }
    except Exception as e:
        logger.warning(f"Could not load existing config: {e}")
        return {"_README": {}, "models_by_name": {}}


# Known OpenRouter-authored frontier models (bleeding edge)
# These may not be in the API yet but can be manually added when available
OPENROUTER_FRONTIER_MODELS = {
    "openrouter/sonoma-dusk-alpha": {
        "aliases": ["sonoma-dusk", "dusk"],
        "context_window": 128000,
        "max_output_tokens": 32000,
        "intelligence_score": 17,
        "description": "OpenRouter Sonoma Dusk Alpha - Bleeding edge frontier model",
    },
    "openrouter/sonoma-sky-alpha": {
        "aliases": ["sonoma-sky", "sky"],
        "context_window": 128000,
        "max_output_tokens": 32000,
        "intelligence_score": 16,
        "description": "OpenRouter Sonoma Sky Alpha - High-performance frontier model",
    },
    "openrouter/horizon-beta": {
        "aliases": ["horizon"],
        "context_window": 200000,
        "max_output_tokens": 64000,
        "intelligence_score": 18,
        "description": "OpenRouter Horizon Beta - Advanced frontier model with large context",
    },
    "openrouter/cypher-alpha": {
        "aliases": ["cypher"],
        "context_window": 128000,
        "max_output_tokens": 32000,
        "intelligence_score": 16,
        "description": "OpenRouter Cypher Alpha - Specialized reasoning model",
    },
}


def should_include_model(model_id: str, api_model: dict) -> bool:
    """Determine if a model should be included in the config.

    Includes alternative, open-source, and specialized models while excluding:
    - Models from providers available via native APIs (OpenAI, Google, Anthropic, X.AI, Perplexity)
    - Free tier limited models (:free suffix)
    - Niche/experimental models from unknown providers
    - Deprecated/old versions

    Args:
        model_id: Model identifier
        api_model: Model data from API

    Returns:
        True if model should be included
    """
    # Exclude free tier variants
    if ":free" in model_id:
        return False

    # Exclude providers available via native APIs (already in openai_models.json, gemini_models.json, xai_models.json)
    # NOTE: X.AI kept here despite having native API because we want Grok code specialist variants
    excluded_providers = {
        "openai",  # Use native OpenAI API instead
        "google",  # Use native Gemini API instead
        "anthropic",  # Use native Claude via Anthropic API instead
        # "x-ai",        # KEEP: Grok-4, Grok Code specialists are valuable
        "perplexity",  # Reasoning/search models - less priority
    }

    provider = model_id.split("/")[0]
    if provider in excluded_providers:
        return False

    # Include major open and specialized model providers
    preferred_providers = {
        # OpenRouter frontier models (bleeding edge)
        "openrouter",  # OpenRouter-authored frontier models
        # Frontier reasoning & specialized
        "x-ai",  # X.AI - Grok models (reasoning + code specialists)
        "minimax",  # MiniMax - 1M+ context frontier model
        # Open source / alternatives
        "mistralai",  # Mistral - major open alternative
        "meta-llama",  # Meta's Llama - largest open model (405B)
        "deepseek",  # DeepSeek - advanced reasoning
        # Chinese LLMs (very capable)
        "qwen",  # Alibaba's Qwen - very capable, excellent code variants
        "z-ai",  # Z-AI - GLM models (Tsinghua)
        "thudm",  # Tsinghua - GLM research models
        "baidu",  # Baidu's models
        "tencent",  # Tencent - major Chinese tech
        "bytedance",  # ByteDance/Douyin - advanced models
        # Research & specialized
        "cohere",  # Cohere - specialized NLP
        "allenai",  # Allen AI - research models
        "ibm-granite",  # IBM's enterprise models
        "microsoft",  # Microsoft research models
        "moonshotai",  # Moonshot - advanced reasoning
        "nousresearch",  # Nous Research - specialized
        "liquid",  # Liquid AI - efficient models
        "nvidia",  # NVIDIA models
    }

    if provider in preferred_providers:
        return True

    # For other providers, only include if they have published pricing and are reasonably named
    pricing = api_model.get("pricing", {})
    if pricing and (pricing.get("prompt") or pricing.get("completion")):
        # Include models with pricing data from providers with longer names (filters noise)
        return len(provider) > 2

    return False


def merge_model_configs(api_models: dict, existing_config: dict, keep_aliases: bool = False) -> list[dict]:
    """Merge API models with curated config data.

    Args:
        api_models: Models from OpenRouter API
        existing_config: Existing config with curated data
        keep_aliases: If True, preserve aliases from existing config

    Returns:
        List of merged model dicts
    """
    merged_models = []
    existing_by_name = existing_config.get("models_by_name", {})

    filtered_count = 0
    included_count = 0

    for model_id, api_model in sorted(api_models.items()):
        if not should_include_model(model_id, api_model):
            filtered_count += 1
            continue

        included_count += 1

        # Start with API-extracted capabilities
        model_config = extract_model_capabilities(api_model)

        # Merge with existing curated data
        if model_id in existing_by_name:
            existing = existing_by_name[model_id]

            # Preserve curated aliases if requested
            if keep_aliases and "aliases" in existing:
                model_config["aliases"] = existing["aliases"]

            # Preserve curated intelligence score only if keep_aliases is True
            if keep_aliases and "intelligence_score" in existing:
                model_config["intelligence_score"] = existing["intelligence_score"]

            # Preserve other curated fields
            for field in [
                "supports_json_mode",
                "supports_function_calling",
                "supports_extended_thinking",
                "supports_images",
                "supports_temperature",
                "temperature_constraint",
                "use_openai_response_api",
                "default_reasoning_effort",
                "allow_code_generation",
            ]:
                if field in existing:
                    model_config[field] = existing[field]

        merged_models.append(model_config)

    logger.info(f"Filtered out {filtered_count} models, keeping {included_count}")
    return merged_models


def generate_readme() -> dict:
    """Generate README section for the config file."""
    return {
        "description": "Model metadata for OpenRouter-backed providers.",
        "documentation": "https://github.com/BeehiveInnovations/zen-mcp-server/blob/main/docs/custom_models.md",
        "usage": "Models listed here are exposed through OpenRouter. Aliases are case-insensitive.",
        "field_notes": "Matches providers/shared/model_capabilities.py.",
        "field_descriptions": {
            "model_name": "The model identifier - OpenRouter format (e.g., 'anthropic/claude-opus-4') or custom model name (e.g., 'llama3.2')",
            "aliases": "Array of short names users can type instead of the full model name",
            "context_window": "Total number of tokens the model can process (input + output combined)",
            "max_output_tokens": "Maximum number of tokens the model can generate in a single response",
            "supports_extended_thinking": "Whether the model supports extended reasoning tokens (currently none do via OpenRouter or custom APIs)",
            "supports_json_mode": "Whether the model can guarantee valid JSON output",
            "supports_function_calling": "Whether the model supports function/tool calling",
            "supports_images": "Whether the model can process images/visual input",
            "max_image_size_mb": "Maximum total size in MB for all images combined (capped at 40MB max for custom models)",
            "supports_temperature": "Whether the model accepts temperature parameter in API calls (set to false for O3/O4 reasoning models)",
            "temperature_constraint": "Type of temperature constraint: 'fixed' (fixed value), 'range' (continuous range), 'discrete' (specific values), or omit for default range",
            "use_openai_response_api": "Set to true when the model must use the /responses endpoint (reasoning models like GPT-5 Pro). Leave false/omit for standard chat completions.",
            "default_reasoning_effort": "Default reasoning effort level for models that support it (e.g., 'low', 'medium', 'high'). Omit if not applicable.",
            "description": "Human-readable description of the model",
            "intelligence_score": "1-20 human rating used as the primary signal for auto-mode model ordering",
            "allow_code_generation": "Whether this model can generate and suggest fully working code - complete with functions, files, and detailed implementation instructions - for your AI tool to use right away. Only set this to 'true' for a model more capable than the AI model / CLI you're currently using.",
        },
    }


def write_config(output_path: str, models: list[dict]) -> None:
    """Write updated config to file.

    Args:
        output_path: Path to write config file to
        models: List of model configs to write
    """
    config = {
        "_README": generate_readme(),
        "models": models,
    }

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    logger.info(f"Updated config written to {output_path}")
    logger.info(f"Total models: {len(models)}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync OpenRouter models from live API to config file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output",
        default="conf/openrouter_models.json",
        help="Output path for config file (default: conf/openrouter_models.json)",
    )
    parser.add_argument(
        "--keep-aliases",
        action="store_true",
        help="Preserve aliases from existing config",
    )
    parser.add_argument(
        "--include-frontier",
        action="store_true",
        help="Include OpenRouter frontier models (even if not yet in API)",
    )

    args = parser.parse_args()

    try:
        # Get OpenRouter API key from environment
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            logger.warning("OPENROUTER_API_KEY not set - requests may be rate-limited")

        # Fetch models from API
        api_models = get_openrouter_models(api_key)

        if not api_models:
            logger.error("No models returned from OpenRouter API")
            sys.exit(1)

        # Add frontier models if requested
        if args.include_frontier:
            logger.info("Including OpenRouter frontier models...")
            for model_id, model_config in OPENROUTER_FRONTIER_MODELS.items():
                if model_id not in api_models:
                    # Create a minimal API model structure for frontier models
                    api_models[model_id] = {
                        "id": model_id,
                        "name": model_config.get("description", model_id),
                        "description": model_config.get("description", ""),
                        "context_length": model_config.get("context_window", 128000),
                        "created": int(__import__("time").time()),
                    }

        # Load existing config for curation data
        existing_config = load_existing_config(args.output)

        # Merge API data with curated config
        merged_models = merge_model_configs(api_models, existing_config, keep_aliases=args.keep_aliases)

        # Add frontier model overrides
        if args.include_frontier:
            for i, model in enumerate(merged_models):
                model_id = model.get("model_name")
                if model_id in OPENROUTER_FRONTIER_MODELS:
                    frontier_config = OPENROUTER_FRONTIER_MODELS[model_id]
                    # Override with frontier model specs
                    merged_models[i].update(frontier_config)

        # Write updated config
        write_config(args.output, merged_models)

        logger.info("✓ Successfully synced OpenRouter models")
        return 0

    except Exception as e:
        logger.error(f"Failed to sync models: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
