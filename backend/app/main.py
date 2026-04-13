from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.routers import project


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="indus.io Backend API",
    description="Backend for the Production Line Simulation Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(project.router)
@app.get("/")
def root():
    return {"message": "Hello World!"}