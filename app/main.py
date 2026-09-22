from fastapi import FastAPI

app = FastAPI(title="Testing API")

@app.get("/")
def root():
    return {
        "status": "success",
        "message": "FastAPI CI/CD pipeline working perfectly!",
        "host": "testing.swapgate-store.com"
    }

@app.get("/health")
def health():
    return {"health": "ok"}