from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from services.database import DataBase

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Get a workflow
    :param workflow_id: str
    :return:  Response
    """
    workflow = database.fetch_workflow(workflow_id)
    return workflow.dict()
