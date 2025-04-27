from typing import Union
from fastapi import FastAPI
from app.db.mongo import client, db
from app.routes import user,folders

app = FastAPI()

app.include_router(user.router, prefix="/api/v1")
app.include_router(folders.router, prefix="/api/v1")


# Dummy API for validating if server is working as expected
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/ping-db")
async def ping_db():
    try:
        await client.admin.command("ping") 
        return {"status": "ok", "message": "Connected to MongoDB"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

 


    