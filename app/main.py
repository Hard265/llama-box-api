from fastapi import FastAPI, APIRouter
from app.database import Base, engine
from app.graphql.schema import graphql_app
from app.api.v1.endpoints.user import router as users_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.share import router as share_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

api_v1_router = APIRouter()

api_v1_router.include_router(users_router, prefix="/users", tags=["users"])
api_v1_router.include_router(share_router, prefix="/s", tags=["shares"])
api_v1_router.include_router(auth_router, prefix="", tags=["authentications", "auth"])

app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])
app.include_router(api_v1_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)