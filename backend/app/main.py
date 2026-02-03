from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, subscriptions, webhooks

app = FastAPI(
    title="LearnHub SaaS API",
    description="SaaS platform with Stripe subscriptions",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(webhooks.router)

@app.get("/")
def read_root():
    return {
        "message": "LearnHub API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "learnhub-backend"
    }