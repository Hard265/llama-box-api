from fastapi import FastAPI
from app.database import Base, engine
from app.graphql.schema import graphql_app

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(graphql_app, prefix="/graphql", tags=["GraphQL"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
