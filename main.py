from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from dotenv import load_dotenv


from databases.fixtures import Fixtures
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from services.database import DataBase
from workflows.base_workflow_dto import WorkflowResponseDTO

app = FastAPI()

load_dotenv()


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
    workflow = WorkflowRepository().fetch_by_id(id)
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
    workflow = WorkflowRepository().fetch_by_id(workflow_id).to_dict()

    workflow_resp = WorkflowResponseDTO()
    workflow_resp.__dict__.update(workflow)
    workflow_resp.nodes = WorkflowNodeRepository().fetch_all_by_workflow_id(workflow_id)
    return workflow_resp.to_dict()

Fixtures().add_test_data(1)
