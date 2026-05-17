from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.chat import router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# SERVE STATIC FILES
app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# SERVE FRONTEND
@app.get("/")
async def root():

    return FileResponse(
        "frontend/index.html"
    )


# API ROUTES
app.include_router(router)
