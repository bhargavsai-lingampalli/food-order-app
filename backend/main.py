from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Request
from backend.routes import menu, cart, order, admin
from fastapi.middleware.cors import CORSMiddleware
from backend import database, models
from backend.utils.websocket import manager
from fastapi.responses import RedirectResponse, JSONResponse
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# CORS middleware to allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:53734"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(menu.router)
import uvicorn

app.include_router(cart.router, prefix="/cart")
app.include_router(order.router, prefix="/order")
app.include_router(admin.router, prefix="/admin")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "620755860055-asse34mj17icr1k43gtn0jg6ruptford.apps.googleusercontent.com")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "GOCSPX-LJAC-359kC65XQQOKEZA")

config = Config(environ={
    "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
    "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
})

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI"),
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = database.database["users"].find_one({"google_id": payload["sub"]})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = str(request.url_for('auth_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    if not user_info:
        return JSONResponse({"error": "Google login failed"}, status_code=400)
    # Store user if new
    user = database.database["users"].find_one({"google_id": user_info["sub"]})
    if not user:
        user_obj = models.User(
            google_id=user_info["sub"],
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture", "")
        )
        database.database["users"].insert_one(user_obj.to_dict())
    # Issue JWT
    access_token = create_access_token({"sub": user_info["sub"]})
    response = RedirectResponse(url="/")
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    return user


@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
