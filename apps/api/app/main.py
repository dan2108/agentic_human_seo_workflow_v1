from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import jobs, gates, content, pipeline, aftercare

app = FastAPI(title="Agentic SEO Workflow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(gates.router, prefix="/gates", tags=["gates"])
app.include_router(content.router, prefix="/content", tags=["content"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(aftercare.router, prefix="/aftercare", tags=["aftercare"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
