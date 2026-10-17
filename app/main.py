from fastapi import FastAPI

from app.api.services import router as services_router


app = FastAPI(title="StatusRadar")
app.include_router(services_router)


@app.get("/health")
def health():
    return {"status": "ok"}
