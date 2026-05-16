from fastapi import FastAPI

from app.routes.chat import router


app = FastAPI(
    title="SHL Assessment Recommendation API"
)


# INCLUDE ROUTES
app.include_router(router)

@app.get("/")
def root():

    return {
        "message": "SHL Assessment Recommendation API Running"
    }
    
# HEALTH CHECK
@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }