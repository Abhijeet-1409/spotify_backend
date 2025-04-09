import uvicorn

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.db.connection import DatabaseConnection
from app.routers import admin,album,auth,song,stat,user
from app.dependencies.dependencies import get_settings, init_cloudinary, init_clerk_sdk


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_instance: DatabaseConnection | None = None
    try :

        settings: Settings  = get_settings()
        db_instance = DatabaseConnection(settings=settings)

        init_cloudinary(settings=settings)

        _ = init_clerk_sdk(settings.CLERK_SECRET_KEY)

        await db_instance.create_index()

        yield

    except Exception as err :
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server is down. Unable to initialize resources."
        )

    finally :
        if db_instance :
            db_instance.close_connection()


app = FastAPI(lifespan=lifespan)

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