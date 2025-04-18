# main.py
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, Railway!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway injects PORT at runtime
    uvicorn.run("main:app", host="0.0.0.0", port=port)
