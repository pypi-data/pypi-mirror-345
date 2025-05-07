from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from .base import MCPBase
from .auth import get_current_active_user, User

router = APIRouter()
bias_scanner = MCPBase()

@router.post("/scan")
@bias_scanner.require_auth(scopes=["bias_scanner"])
async def scan_text(
    text: str,
    current_user: User = get_current_active_user
) -> Dict[str, Any]:
    """
    Analiza el texto en busca de sesgos
    
    Args:
        text: Texto a analizar
        current_user: Usuario autenticado
        
    Returns:
        Dict con el resultado del análisis
    """
    try:
        # TODO: Implementar el análisis real de sesgos
        bias_score = 0.5  # Placeholder
        return {
            "bias_score": bias_score,
            "analysis": "Análisis de sesgos realizado",
            "user": current_user.username
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el análisis de sesgos: {str(e)}"
        )

app = router 