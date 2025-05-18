import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from src.api_v1 import router as api_router
from src.core.config import configure_logging

description = """
    API library management

    You will be able to:

    * **Read users**
    * **Create/Update/Remove users**
    * **book delivery/return**
"""

app = FastAPI(
    title="API_ManagementLibrary",
    description=description,
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_router)

configure_logging(logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
