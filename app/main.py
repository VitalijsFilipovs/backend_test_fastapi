from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import User
from .schemas import RegisterRequest, UserOut, LoginRequest, TokenResponse
from .utils import hash_password, verify_password
from .auth import create_access_token
from .deps import get_current_user
from fastapi.middleware.cors import CORSMiddleware
import logging

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend Test API", version="1.0.0")

# CORS: разрешим локальные фронты и postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # сузить на проде
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# простое логирование запросов
logger = logging.getLogger("uvicorn.access")

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"-> {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)

@app.get("/public-data")
def public_data():
    return {"data": "Публичная информация доступна всем"}

@app.get("/private-data")
def private_data(current_user: User = Depends(get_current_user)):
    return {"data": f"Приватная информация для {current_user.email}"}
