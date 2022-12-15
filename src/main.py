from uvicorn import run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import (
    SITE_PORT,
    SITE_HOST,
    PROJECT_TITLE,
)
from routers import api_router


app = FastAPI(title=PROJECT_TITLE)
app.add_middleware(
    CORSMiddleware,
    allow_origins="origins",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

if __name__ == "__main__":
    run(
        "main:app",
        port=SITE_PORT,
        host=SITE_HOST,
        reload=True,
        forwarded_allow_ips="*",
    )

