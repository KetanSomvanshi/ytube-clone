#!/usr/bin/env python3
from fastapi import FastAPI

from controller import status
from logger import logger
from server.auth import authenticate
import uvicorn

app = FastAPI()

app.include_router(status.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=6006, reload=True)
