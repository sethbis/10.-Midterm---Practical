from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import router

app = FastAPI(
    title="AWS Cloud URL Shortener API",
    description="Scalable cloud URL Shortener powered by FastAPI, Amazon DynamoDB, EC2 and S3.",
    version="1.0.0",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Monitoring"], summary="Health check endpoint")
def health_check():
    """Simple health check endpoint for EC2 and monitoring services."""
    return {
        "status": "healthy",
        "service": "aws-url-shortener",
        "dynamodb_table": settings.DYNAMODB_TABLE_NAME,
        "region": settings.AWS_REGION,
    }


# Include business routes
app.include_router(router)
