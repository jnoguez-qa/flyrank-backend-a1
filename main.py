from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, Field
from auth_config import supabase

app = FastAPI(
    title="FlyRank Auth API",
    description="Authentication API with Supabase Auth for FlyRank Internship",
    version="1.0"
)


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
    # 1. Input Validation: Check for empty or whitespace-only credentials
    clean_email = payload.email.strip()
    clean_password = payload.password.strip()

    if not clean_email or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password cannot be empty"}
        )

    # 2. Call Supabase Auth SDK signUp
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
    # 1. Input Validation: Check for empty fields
    clean_email = payload.email.strip()
    clean_password = payload.password.strip()

    if not clean_email or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Email and password cannot be empty"}
        )

    # 2. Call Supabase Auth SDK signInWithPassword
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
        # Supabase throws an exception on wrong password/unregistered email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid login credentials"}
        )

    from fastapi import Request

# ============================================================================
# Stage 2 — Public & Protected Gates
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
def get_protected_profile(request: Request):
    # 1. Extraer encabezado Authorization
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )

    # 2. Extraer el string del token
    token = auth_header.split(" ")[1]

    # 3. Validar el token directamente con Supabase
    try:
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid or expired token"}
            )

        # 4. Retornar la metadata segura del usuario verificado
        user = user_response.user
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Invalid or expired token"}
        )