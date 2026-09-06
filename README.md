# FlyRank Auth API (FastAPI + Supabase Auth)

A lightweight, production-ready, modular, and secure backend authentication system built with **FastAPI** (Python 3.12+) and integrated with **Supabase Auth**. This project implements end-to-end user lifecycle management, JSON Web Token (JWT) verification, custom dependency middleware for protected route guards, and full Swagger UI / OpenAPI integration with Bearer Authorization.

---

## 🛠️ Tech Stack & Architecture

* **Language:** Python 3.12+
* **Web Framework:** FastAPI (v0.110+)
* **ASGI Server:** Uvicorn
* **Authentication & BaaS:** Supabase Auth Python SDK
* **Data Validation & Schemas:** Pydantic v2 (utilizing `EmailStr` and field specifications via `email-validator`)
* **Environment Configuration:** Python-Dotenv
* **Documentation & Testing:** Interactive Swagger UI / OpenAPI 3.0 (configured with HTTP Bearer Auth security scheme)

---

## 📁 Project Structure

flyrank-backend-a1/
│
├── auth_config.py     # Global Supabase client initialization using environment variables
├── main.py            # FastAPI entry point, Pydantic models, reusable dependencies, and end-to-end routes
├── .env               # Private environment variables configuration file (git-ignored)
├── .gitignore         # Exclusion list covering virtual environments, secrets, and system cache
└── README.md          # Comprehensive technical documentation and setup guide

---

## ⚙️ Environment Variables

Before launching the application, create a `.env` file in the root project directory containing your Supabase project credentials. You can retrieve these values directly from your Supabase Dashboard under `Project Settings -> API`:

| Variable | Type | Description |
| :--- | :--- | :--- |
| `SUPABASE_URL` | String | Your unique Supabase project URL (e.g., `https://<project-ref>.supabase.co`) |
| `SUPABASE_KEY` | String | Your Supabase public anonymous API key (`anon` key) |

---

## 🚀 Installation & Local Development Setup

Follow these sequential steps to set up, configure, and execute the backend application locally using PowerShell on Windows or standard Unix terminals:

1. **Clone the remote GitHub repository:**
   git clone https://github.com/jnoguez-qa/flyrank-backend-a1.git
   cd flyrank-backend-a1

2. **Initialize and activate the Python virtual environment (`venv`):**
   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. **Install all required dependencies and packages:**
   pip install fastapi uvicorn supabase email-validator python-dotenv

4. **Verify environment setup and boot the local ASGI Uvicorn development server:**
   uvicorn main:app --reload --port 8000

Once initialized, the local API instance will be actively running and listening at `http://localhost:8000`.

---

## 📌 Complete API Endpoint Reference

### 🔓 Public Endpoints (Unrestricted Access)

| HTTP Method | Endpoint Path | Summary | Description | Expected Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Root Verification | Server vitality check confirming Supabase connection status | `200 OK` |
| `GET` | `/public/info` | Public Data | Open informational endpoint requiring no authorization header | `200 OK` |
| `POST` | `/auth/signup` | User Registration | Registers a new user account in Supabase using sanitized credentials | `201 Created` |
| `POST` | `/auth/login` | User Authentication | Validates user credentials and returns an active JWT `access_token` and `refresh_token` | `200 OK` |

### 🔒 Protected Endpoints (Requires `Authorization: Bearer <JWT_TOKEN>`)

| HTTP Method | Endpoint Path | Summary | Description | Expected Status |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/protected/profile` | Profile Metadata | Verifies incoming JWT directly via Supabase Auth and returns user metadata | `200 OK` |
| `GET` | `/protected/dashboard` | Private Dashboard | Demonstrates modular middleware reuse using FastAPI's `Depends(get_current_user)` | `200 OK` |
| `POST` | `/auth/logout` | Session Termination | Invalidates the active user session and logs out the authenticated user | `204 No Content` |

---

## 🛡️ Authentication Architecture & Middleware Security

The application utilizes FastAPI's dependency injection system (`Depends`) to enforce rigid token validation policies across all protected endpoints:

1. **Header Parsing:** The `get_current_user` dependency automatically intercepts incoming requests and extracts the `Authorization: Bearer <TOKEN>` header via `HTTPBearer`.
2. **Cryptographic Validation:** The extracted JWT is submitted directly to `supabase.auth.get_user(token)` to verify its signature, authenticity, and expiration state against the Supabase backend.
3. **Payload Injection:** Upon successful verification, the user payload and active session token are injected directly into the route handler, guaranteeing zero unauthenticated leakages (`401 Unauthorized` raised on invalid or tampered tokens).

---

## 🧪 Verification & Endpoint Testing via `curl`

To execute end-to-end endpoint verification directly from your PowerShell console, follow this test workflow:

### 1. Register a new user account (`POST /auth/signup`)
curl.exe -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{\"email\":\"user@example.com\", \"password\":\"password123\"}'

### 2. Authenticate and retrieve active JWT tokens (`POST /auth/login`)
curl.exe -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{\"email\":\"user@example.com\", \"password\":\"password123\"}'

### 3. Query protected profile data (`GET /protected/profile`)
curl.exe -i http://localhost:8000/protected/profile -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"

### 4. Query protected dashboard endpoint (`GET /protected/dashboard`)
curl.exe -i http://localhost:8000/protected/dashboard -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"

### 5. Terminate active user session (`POST /auth/logout`)
curl.exe -i -X POST http://localhost:8000/auth/logout -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"

---

## 📖 Interactive OpenAPI & Swagger UI Documentation

The backend includes native OpenAPI integration pre-configured for Bearer Token authorization:

1. Open your browser and navigate to `http://localhost:8000/docs`.
2. Click on the **`POST /auth/login`** endpoint, execute it with valid user credentials, and copy the returned `access_token`.
3. Scroll to the top right of the Swagger UI interface and click the **Authorize 🔓** button.
4. Paste your `access_token` into the Value field and click **Authorize**.
5. All protected endpoints (`/protected/profile`, `/protected/dashboard`, and `/auth/logout`) are now unlocked and can be tested interactively directly from the UI.