from fastapi import FastAPI
import uvicorn
from api.v1.main import router as api_router_v1

app = FastAPI()

app.include_router(api_router_v1, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)