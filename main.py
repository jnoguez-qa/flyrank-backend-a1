from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from auth_config import supabase

app = FastAPI(
    title="FlyRank Auth API",
    description="Authentication API with Supabase Auth for FlyRank Internship",
    version="1.0"
)

# Esquema de seguridad Bearer Token para Swagger UI (/docs)
security = HTTPBearer()


# ============================================================================
# Schemas (Pydantic Models)
# ============================================================================
class UserAuthSchema(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


# ============================================================================
# Lifespan / Startup Verification (Stage 0)
# ============================================================================
@app.on_event("startup")
def startup_event():
    print("Server running and connected to Supabase")


@app.get("/", tags=["System"])
def read_root():
    return {
        "message": "Server running and connected to Supabase",
        "docs": "/docs"
    }


# ============================================================================
# Stage 1 — Open Auth Routes (Sign Up & Log In)
# ============================================================================

@app.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
    tags=["Auth"]
)
def signup(payload: UserAuthSchema):
    clean_email = payload.email.strip()
    clean_password = payload.password.strip()

    if not clean_email or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password cannot be empty"}
        )

    try:
        response = supabase.auth.sign_up({
            "email": clean_email,
            "password": clean_password
        })

        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "User creation failed"}
            )

        return response.user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )


@app.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate user & return JWT",
    tags=["Auth"]
)
def login(payload: UserAuthSchema):
    clean_email = payload.email.strip()
    clean_password = payload.password.strip()

    if not clean_email or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password cannot be empty"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": clean_email,
            "password": clean_password
        })

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid login credentials"}
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
            "user": response.user
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )


# ============================================================================
# Stage 4 & 5 — Guard Dependency & Swagger Authorization
# ============================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Reusable Dependency Guard to verify JWT with Supabase and activate Swagger Bearer Auth"""
    token = credentials.credentials

    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"}
            )
        return {"user": user_response.user, "token": token}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )


# ============================================================================
# Stage 2 & 4 — Public & Protected Endpoints
# ============================================================================

@app.get(
    "/public/info",
    status_code=status.HTTP_200_OK,
    summary="Read public, unprotected data",
    tags=["Public"]
)
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get(
    "/protected/profile",
    status_code=status.HTTP_200_OK,
    summary="Read private user profile data",
    tags=["Protected"]
)
def get_protected_profile(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


@app.get(
    "/protected/dashboard",
    status_code=status.HTTP_200_OK,
    summary="Second protected route to verify middleware reuse",
    tags=["Protected"]
)
def get_protected_dashboard(auth_data: dict = Depends(get_current_user)):
    user = auth_data["user"]
    return {
        "message": f"Welcome to your private dashboard, {user.email}!"
    }


@app.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate the user session",
    tags=["Auth"]
)
def logout(auth_data: dict = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e)}
        )