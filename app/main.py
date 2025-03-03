import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import admin,album,auth,song,stat,user

app = FastAPI()

app.include_router(admin.router)
app.include_router(album.router)
app.include_router(auth.router)
app.include_router(song.router)
app.include_router(stat.router)
app.include_router(user.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)