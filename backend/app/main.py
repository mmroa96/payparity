from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import benchmark

app = FastAPI(title="PayParity API", version="0.1.0-alpha")

# TECH DEBT: wide-open CORS for local Alpha development against the
# Vite/CRA dev server. Needs to be locked to the deployed frontend
# origin before this goes anywhere near production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(benchmark.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
