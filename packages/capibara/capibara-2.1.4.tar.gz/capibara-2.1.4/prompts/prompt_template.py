"""
Enhanced Prompt Templates for CapibaraModel with Advanced Generation Capabilities
"""

from typing import Dict, Any, Optional, Tuple
import jax #type: ignore
import jax.numpy as jnp #type: ignore
from flax import linen as nn #type: ignore
import logging
import time

# Assume these are imported from project modules
from capibara_model.core.tokenizer import tokenize_text, decode_tokens  # type: ignore
from capibara_model.core.model import CapibaraModel  # type: ignore

logger = logging.getLogger(__name__)

# Enhanced prompt templates with markdown formatting
PROMPT_TEMPLATES = {
    "summary": {
        "prompt": "Generate a comprehensive summary of the following content:",
        "format_config": {
            "title": "Detailed Summary",
            "subtitle": "Key Information Extraction",
            "sections": {
                "main_points": True,
                "key_terms": True,
                "action_items": False,
                "conclusions": True
            },
            "structure": "hierarchical"
        }
    },
    "step_by_step": {
        "prompt": "Provide a detailed step-by-step explanation for:",
        "format_config": {
            "title": "Process Breakdown",
            "subtitle": "Sequential Instructions",
            "sections": {
                "materials_needed": True,
                "precautions": True,
                "steps": True,
                "troubleshooting": True
            },
            "structure": "numbered"
        }
    }
}

def decode_logits_to_text(
    logits: jnp.ndarray,
    temperature: float = 0.7,
    top_p: float = 0.9,
    eos_token_id: int = 50256
) -> Tuple[str, jnp.ndarray]:
    """
    Enhanced text decoding with proper nucleus sampling and validation
    
    Args:
        logits: Model output logits (batch_size, seq_len, vocab_size)
        temperature: Sampling temperature (0 < temp ≤ 2.0)
        top_p: Nucleus sampling probability (0 < top_p ≤ 1.0)
        eos_token_id: End-of-sequence token ID
    
    Returns:
        Tuple containing decoded text and final tokens
    """
    # Input validation
    if logits.ndim != 3:
        raise ValueError(f"Logits must be 3D (batch, seq, vocab). Got: {logits.ndim}D")
    
    if temperature <= 0 or temperature > 2.0:
        raise ValueError(f"Temperature must be 0 < temp ≤ 2.0. Got: {temperature}")
    
    if top_p <= 0 or top_p > 1.0:
        raise ValueError(f"top_p must be 0 < top_p ≤ 1.0. Got: {top_p}")

    # Convert to probabilities
    scaled_logits = logits / jnp.maximum(temperature, 1e-6)
    probs = jax.nn.softmax(scaled_logits, axis=-1)

    # Efficient nucleus sampling implementation
    def _nucleus_sampling(probs):
        sorted_indices = jnp.argsort(-probs)
        sorted_probs = probs[sorted_indices]
        cum_probs = jnp.cumsum(sorted_probs)
        mask = cum_probs <= top_p
        mask = jnp.concatenate([jnp.array([True]), mask[:-1]])  # Include first element
        
        # Filter and renormalize
        filtered_probs = jnp.where(mask, sorted_probs, 0.0)
        filtered_probs /= jnp.sum(filtered_probs)
        
        # Return to original indices
        return jnp.zeros_like(probs).at[sorted_indices].set(filtered_probs)

    # Vectorize over batch and sequence dimensions
    processed_probs = jax.vmap(jax.vmap(_nucleus_sampling))(probs)

    # Generate unique seed based on current time
    seed = int(time.time() * 1e6) % (2**32 - 1)
    tokens = jax.random.categorical(
        jax.random.PRNGKey(seed),
        jnp.log(processed_probs),
        axis=-1
    )

    # Find EOS tokens and truncate
    eos_positions = jnp.argmax(tokens == eos_token_id, axis=1)
    output_tokens = jnp.where(
        jnp.arange(tokens.shape[1])[None, :] <= eos_positions[:, None],
        tokens,
        jnp.full_like(tokens, eos_token_id)
    )

    return decode_tokens(output_tokens), output_tokens

def generate_formatted_response(
    model: CapibaraModel,
    params: Dict[str, Any],
    user_query: str,
    request_type: str,
    context: Optional[jnp.ndarray] = None,
    max_length: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    num_beams: int = 1,
    repetition_penalty: float = 1.2
) -> str:
    """
    Enhanced autoregressive generation with template formatting
    
    Args:
        model: Initialized CapibaraModel instance
        params: Model parameters
        user_query: Input text from user
        request_type: Key from PROMPT_TEMPLATES
        context: Optional context tensor (batch, seq, features)
        max_length: Maximum generation length
        temperature: Sampling temperature
        top_p: Nucleus sampling probability
        num_beams: Number of beams for beam search
        repetition_penalty: Penalty for repeated tokens
    
    Returns:
        Formatted response text with markdown structure
    """
    # Validate template
    template_info = PROMPT_TEMPLATES.get(request_type)
    if not template_info:
        valid_types = ", ".join(PROMPT_TEMPLATES.keys())
        raise ValueError(f"Invalid request_type: {request_type}. Valid types: {valid_types}")

    # Construct formatted prompt
    default_config = {
        'title': 'Response',
        'subtitle': '',
        'sections': {}
    }
    format_config = template_info.get("format_config", default_config)
    if not isinstance(format_config, dict):
        format_config = default_config
        
    formatted_prompt = _construct_prompt(
        str(template_info["prompt"]),
        user_query,
        format_config
    )

    # Tokenize with special handling
    input_tokens = tokenize_text(formatted_prompt, add_special_tokens=True)
    input_tokens = jnp.array(input_tokens)[None, :]  # Add batch dimension

    # Generation loop
    generated_tokens = input_tokens
    for _ in range(max_length):
        # Get model predictions
        logits = model.apply(
            {'params': params},
            generated_tokens,
            context,
            training=False,
            mutable=False
        )

        # Apply repetition penalty
        logits = _apply_repetition_penalty(logits, generated_tokens, repetition_penalty)

        # Sample next tokens
        next_tokens = decode_logits_to_text(
            logits[:, -1, :][:, None, :],  # Add sequence dimension
            temperature=temperature,
            top_p=top_p
        )[1]

        # Concatenate new tokens
        generated_tokens = jnp.concatenate(
            [generated_tokens, next_tokens[:, -1:]], 
            axis=-1
        )

        # Check stopping condition
        if next_tokens[0, -1] == model.config.eos_token_id:
            break

    # Decode and format
    raw_response = decode_tokens(generated_tokens[0])
    
    # Asegurar que format_config sea un diccionario
    default_config = {
        'title': 'Response',
        'subtitle': '',
        'sections': {}
    }
    format_config = template_info.get("format_config", default_config)
    if not isinstance(format_config, dict):
        format_config = default_config
        
    return _format_response(raw_response, format_config)

def _construct_prompt(
    instruction: str,
    query: str,
    format_config: Dict[str, Any]
) -> str:
    """Build structured prompt with markdown formatting"""
    sections = [
        f"# {format_config['title']}",
        f"## {format_config['subtitle']}" if format_config.get('subtitle') else "",
        "### Instruction",
        instruction,
        "### Query",
        query,
        "### Response\n"
    ]
    return "\n".join(filter(None, sections))

def _format_response(raw_text: str, format_config: Dict[str, Any]) -> str:
    """Apply template-based formatting to raw model output"""
    structured_sections = []
    
    # Add header
    structured_sections.append(f"# {format_config['title']}")
    if format_config.get('subtitle'):
        structured_sections.append(f"## {format_config['subtitle']}")
    
    # Add sections based on config
    sections = format_config['sections']
    if sections.get('main_points'):
        structured_sections.append("### Key Points\n" + _extract_section(raw_text, 'points'))
    if sections.get('steps'):
        structured_sections.append("## Procedure\n" + _format_steps(raw_text))
    if sections.get('conclusions'):
        structured_sections.append("## Final Conclusions\n" + _extract_section(raw_text, 'conclusions'))
    
    return "\n\n".join(structured_sections)

def _apply_repetition_penalty(
    logits: jnp.ndarray,
    generated_tokens: jnp.ndarray,
    penalty: float
) -> jnp.ndarray:
    """Apply repetition penalty to logits"""
    token_counts = jnp.bincount(generated_tokens.flatten(), length=logits.shape[-1])
    return logits - (token_counts * penalty)

def _extract_section(text: str, section_type: str) -> str:
    """Helper to extract relevant sections from raw text"""
    # Implementation depends on model's response patterns
    return text  # Simplified for example

def _format_steps(text: str) -> str:
    """Format step-by-step instructions"""
    return "\n".join([f"{i+1}. {line}" for i, line in enumerate(text.split('\n')) if line.strip()])

# Example Usage
if __name__ == "__main__":
    # Initialize model and tokenizer (mock implementation)
    class TestModel(CapibaraModel):
        def apply(self, params, inputs, context, training):
            return jax.random.normal(jax.random.PRNGKey(0), (inputs.shape[0], inputs.shape[1], 50257))
    
    model = TestModel()
    params = {"dummy": "params"}
    
    # Generate formatted response
    response = generate_formatted_response(
        model=model,
        params=params,
        user_query="Explain the process of photosynthesis in tropical plants.",
        request_type="step_by_step",
        max_length=100,
        temperature=0.8,
        top_p=0.95
    )
    
    print("Generated Response:")
    print(response)