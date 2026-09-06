from fastapi import FastAPI, HTTPException, status
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