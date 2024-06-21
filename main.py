import asyncio
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from services.database import DataBase

app = FastAPI()
database: DataBase = DataBase()


@app.get("/")
async def root():
    return {"message": "Hello World"}


class WorkflowRunRequest(BaseModel):
    id: str


@app.post("/workflow/run")
async def run_workflow(request: WorkflowRunRequest):
    """
    Run a workflow
    :param request: WorkflowRunRequest
    :return:  Response

    This currently only supports serial execution of the workflow
    """
    id = request.id
    # Fetch the workflow
    workflow = database.fetch_workflow(id)
    await workflow.execute()

    return {
        "response": "success"
    }
