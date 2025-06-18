from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def hello():
    return {"msg": "Hi!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)