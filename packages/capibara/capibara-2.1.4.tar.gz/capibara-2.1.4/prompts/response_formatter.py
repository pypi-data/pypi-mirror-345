"""
Enhanced Markdown Formatting Utilities for Model Responses

This module provides structured formatting with validation and improved type handling.
"""

from typing import List, Optional, Union
from utils.error_handling import (
    BaseConfig,
    handle_error,
    DataProcessingError
)

class MarkdownSection(BaseConfig):
    """Base model for Markdown section validation"""
    content: Union[str, List[str]]
    enabled: bool = True

class MarkdownResponse(BaseConfig):
    """Model for complete Markdown response validation"""
    sections: List[MarkdownSection]
    metadata: Optional[dict] = None

@handle_error(DataProcessingError)
def format_markdown_response(
    content: Union[str, List[str]],
    metadata: Optional[dict] = None
) -> str:
    """
    Formatea una respuesta en Markdown con validación.
    
    Args:
        content: Contenido a formatear
        metadata: Metadatos adicionales
        
    Returns:
        Respuesta formateada en Markdown
    """
    # Crear sección
    section = MarkdownSection(content=content)
    
    # Crear respuesta
    response = MarkdownResponse(
        sections=[section],
        metadata=metadata
    )
    
    # Formatear
    formatted = []
    for section in response.sections:
        if section.enabled:
            if isinstance(section.content, list):
                formatted.extend(section.content)
            else:
                formatted.append(section.content)
    
    return "\n\n".join(formatted)

@handle_error(DataProcessingError)
def validate_markdown_response(response: str) -> bool:
    """
    Valida una respuesta en Markdown.
    
    Args:
        response: Respuesta a validar
        
    Returns:
        True si la respuesta es válida
    """
    try:
        # Intentar crear objeto de respuesta
        MarkdownResponse(sections=[MarkdownSection(content=response)])
        return True
    except Exception:
        return False

# Example Usage
if __name__ == "__main__":
    try:
        formatted = format_markdown_response(
            content="Quantum Computing Basics",
            metadata={
                "title": "An Introductory Overview",
                "paragraphs": [
                    "Quantum computing leverages quantum mechanical phenomena to perform computations.",
                    "Qubits can exist in superposition states enabling parallel processing."
                ],
                "summary": "Fundamental concepts of quantum computation",
                "important_points": [
                    "Uses qubits instead of classical bits",
                    "Employs superposition and entanglement",
                    "Enables exponential computational speedups for certain problems"
                ],
                "final_summary": "Quantum computing represents a paradigm shift in computational theory"
            }
        )
        
        print("Formatted Markdown:\n")
        print(formatted)
    
    except ValueError as ve:
        print(f"Validation Error: {ve}")
    except RuntimeError as re:
        print(f"Runtime Error: {re}")