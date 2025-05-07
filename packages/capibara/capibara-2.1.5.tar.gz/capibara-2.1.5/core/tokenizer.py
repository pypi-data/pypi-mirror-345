"""
Módulo de tokenización para CapibaraModel.
"""
from typing import List, Union, Optional, Dict, Any, Literal
import numpy as np # type: ignore
import jax.numpy as jnp # type: ignore
from transformers import AutoTokenizer # type: ignore
from transformers.tokenization_utils_base import PreTrainedTokenizerBase # type: ignore

def load_tokenizer(model_name: str = "gpt2") -> PreTrainedTokenizerBase:
    """
    Carga un tokenizador pre-entrenado.
    
    Args:
        model_name: Nombre del modelo pre-entrenado
        
    Returns:
        Tokenizador cargado
    """
    return AutoTokenizer.from_pretrained(model_name)

def tokenize_text(
    text: Union[str, List[str]], 
    tokenizer: PreTrainedTokenizerBase,
    max_length: Optional[int] = None,
    padding: bool = False,
    truncation: bool = False,
    return_tensors: Literal["np"] = "np",
    return_attention_mask: Optional[bool] = None,
    return_token_type_ids: bool = False
) -> Union[jnp.ndarray, Dict[str, jnp.ndarray]]:
    """
    Tokeniza texto(s) con opciones configurables.
    
    Args:
        text: Texto o lista de textos a tokenizar
        tokenizer: Tokenizador a usar
        max_length: Longitud máxima de secuencia
        padding: Si se debe aplicar padding. Si es True, también devuelve attention_mask
        truncation: Si se debe truncar secuencias largas
        return_tensors: Formato de retorno (solo se admite "np" por compatibilidad con JAX)
        return_attention_mask: Si se debe devolver attention mask (por defecto igual a padding)
        return_token_type_ids: Si se deben devolver token type IDs (solo para modelos que los requieren)
        
    Returns:
        Array de tokens o diccionario con arrays de tokens y attention masks (si padding=True)
    """
    assert return_tensors == "np", "Solo se admite 'np' por compatibilidad con JAX"
    
    is_batch = isinstance(text, list)
    return_attention_mask = padding if return_attention_mask is None else return_attention_mask
    
    if is_batch:
        encoded = tokenizer(
            text,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors=return_tensors,
            return_attention_mask=return_attention_mask,
            return_token_type_ids=return_token_type_ids
        )
        return {k: jnp.array(v).astype(jnp.int32) for k, v in encoded.items()}
    else:
        encoded = tokenizer(
            text,
            max_length=max_length,
            padding=padding,
            truncation=truncation,
            return_tensors=return_tensors,
            return_attention_mask=return_attention_mask,
            return_token_type_ids=return_token_type_ids
        )
        return jnp.array(encoded["input_ids"][0]).astype(jnp.int32)

def decode_tokens(
    tokens: Union[jnp.ndarray, List[int], Dict[str, jnp.ndarray]], 
    tokenizer: PreTrainedTokenizerBase,
    skip_special_tokens: bool = True
) -> Union[str, List[str]]:
    """
    Decodifica tokens a texto(s).
    
    Args:
        tokens: Tokens a decodificar (puede ser array, lista o diccionario)
        tokenizer: Tokenizador a usar
        skip_special_tokens: Si se deben omitir tokens especiales
        
    Returns:
        Texto o lista de textos decodificados
    """
    if isinstance(tokens, dict):
        # Si es un batch con attention mask
        input_ids = tokens["input_ids"]
        if len(input_ids.shape) > 1:
            return tokenizer.batch_decode(
                input_ids,
                skip_special_tokens=skip_special_tokens
            )
        return tokenizer.decode(
            input_ids[0],
            skip_special_tokens=skip_special_tokens
        )
    
    if isinstance(tokens, jnp.ndarray):
        if len(tokens.shape) > 1:
            # Batch de tokens
            return tokenizer.batch_decode(
                tokens,
                skip_special_tokens=skip_special_tokens
            )
        tokens = tokens.tolist()
    
    return tokenizer.decode(
        tokens,
        skip_special_tokens=skip_special_tokens
    )

def pad_and_tokenize(
    texts: List[str],
    tokenizer: PreTrainedTokenizerBase,
    max_length: Optional[int] = None
) -> Dict[str, jnp.ndarray]:
    """
    Utilidad para preparar batches con padding automático.
    
    Args:
        texts: Lista de textos a tokenizar
        tokenizer: Tokenizador a usar
        max_length: Longitud máxima de secuencia
        
    Returns:
        Diccionario con arrays de tokens y attention masks
    """
    return tokenize_text(
        text=texts,
        tokenizer=tokenizer,
        max_length=max_length,
        padding=True,
        truncation=True,
        return_tensors="np"
    ) 