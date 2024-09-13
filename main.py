from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import greenfootapi.models as m
from greenfootapi.database import engine
from greenfootapi.routers import users, trees, admin, utils, images, analytics
from fastapi.staticfiles import StaticFiles

app = FastAPI()
m.Base.metadata.create_all(bind=engine)

app.mount("/tree_images", StaticFiles(directory="tree_images"), name="tree_images")
app.include_router(users.router)
app.include_router(trees.router)
app.include_router(admin.router)
app.include_router(utils.router)
app.include_router(images.router)
app.include_router(analytics.router)

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


