from fastapi import FastAPI

app = FastAPI(title="StatusRadar")


@app.get("/health")
def health():
    return {"status": "ok"}