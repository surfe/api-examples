from typing import Union

from fastapi import FastAPI # type: ignore
from app.webhook.handler import router as webhook_router

app = FastAPI(title="C-Level Priority Handler")


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)