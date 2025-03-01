# /Users/1byinf8/Documents/quant-api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from routes.api import router, sio

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", socketio.ASGIApp(sio))
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)