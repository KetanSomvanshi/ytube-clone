#!/usr/bin/env python3
from fastapi import FastAPI, Depends

from controller import status
from controller import ytube_controller
from data_adapter import db
from logger import logger
from server.auth import authenticate
import uvicorn

app = FastAPI()

db.DBBase.metadata.create_all(bind=db.db_engine)

app.include_router(status.router)
app.include_router(ytube_controller.video_router, dependencies=[Depends(authenticate)])


@app.on_event("startup")
async def startup_event():
    logger.info("Startup Event Triggered")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown Event Triggered")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=6006, reload=True)
