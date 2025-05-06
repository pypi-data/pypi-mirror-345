import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from .utils.cache import cache

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "bias_scanner": "Acceso al escáner de sesgos",
        "creativity_checker": "Acceso al verificador de creatividad",
        "doc_retriever": "Acceso al recuperador de documentos",
        "health_advisor": "Acceso al asesor de salud",
        "image_interpreter": "Acceso al intérprete de imágenes",
        "sql_tool": "Acceso a la herramienta SQL",
        "veracity_verifier": "Acceso al verificador de veracidad",
        "evidence_search": "Acceso al buscador de evidencias",
    }
)

# Modelos de datos
class TokenData(BaseModel):
    username: str
    scopes: list[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: list[str] = []

class UserInDB(User):
    hashed_password: str

# Funciones de utilidad
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Configuración de JWT
SECRET_KEY = os.getenv("CAPIBARA_MCP_SECRET") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Verificar token en caché primero
        cached_user = cache.get(f"token_{token}")
        if cached_user:
            return User(**cached_user)
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
        
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
            
    # Cachear el usuario
    cache.put(f"token_{token}", user.dict())
    return user

async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=[])
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# TODO: Implementar la conexión real con la base de datos
async def get_user(username: str) -> Optional[UserInDB]:
    # Esto es un placeholder - en producción debería conectarse a una base de datos
    if username == "test_user":
        return UserInDB(
            username=username,
            hashed_password=get_password_hash("test_password"),
            scopes=["bias_scanner", "creativity_checker"]
        )
    return None 