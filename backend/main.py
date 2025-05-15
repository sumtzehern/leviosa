
from routes import ocr_routes
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
import os
from dotenv import load_dotenv   # type: ignore

load_dotenv(override=True)
print(f"OPENAI_API_KEY loaded: {'OPENAI_API_KEY' in os.environ}")

from fastapi import FastAPI # type: ignore
from routes import upload

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# for api documentation
# http://localhost:8000/redoc
# http://localhost:8000/docs

app = FastAPI(
    title="Leviosa AI API",
    description="API for document parsing and text extraction",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],  # Frontend Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the uploads directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(ocr_routes.router, prefix="/api", tags=["Parse"])

@app.get("/")
async def root():
    return {"message": "Welcome to Leviosa AI API"}

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
