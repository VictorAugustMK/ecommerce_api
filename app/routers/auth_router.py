from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.models import User, UserLogin, RefreshToken
from app.auth import get_current_user
from app.db.session import get_db as Session
from app.auth.dependencies.admin_setup_router import SECRET_KEY, ALGORITHM
from app.auth.services.jwt_service import create_access_token, create_refresh_token

auth_router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@auth_router.post("/register")
def register(user: User):
    conn = get_current_user()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Usuário já existe")

    hashed_password = pwd_context.hash(user.password)
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        (user.username, user.email, hashed_password)
    )
    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Usuário registrado com sucesso"}

@auth_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_current_user)):
    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token, jti, expires_at = create_refresh_token({"sub": user.username, "role": user.role})

    db.add(RefreshToken(
        user_id=user.id,
        token=jti,
        expires_at=expires_at
    ))
    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}

@auth_router.post("/refresh-token")
def refresh_token(request: RefreshToken, db: Session = Depends(get_current_user)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        jti: str = payload.get("jti")

        if not username or not role or not jti:
            raise HTTPException(status_code=401, detail="Token inválido")

        token_in_db = db.query(RefreshToken).filter_by(token=jti).first()
        if not token_in_db or token_in_db.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

        new_access_token = create_access_token({"sub": username, "role": role})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Token de refresh inválido ou expirado")

