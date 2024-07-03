from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from dotenv import load_dotenv


from databases.fixtures import Fixtures
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from services.workflow import WorkflowService
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

@app.get("/")
async def root():
    return {"message": "Hello World"}


class WorkflowRunRequest(BaseModel):
    id: str
    nodes: list | None = None


@app.post("/workflow/run")
async def run_workflow(request: WorkflowRunRequest):
    """
    Run a workflow
    :param request: WorkflowRunRequest
    :return:  Response

    This currently only supports serial execution of the workflow
    """
    workflow_id = request.id
    nodes = request.nodes
    workflow = WorkflowRepository().fetch_by_id(workflow_id)
    workflow_service = WorkflowService(workflow=workflow)
    await workflow_service.execute(nodes)
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
    workflow = WorkflowRepository().fetch_by_id(workflow_id)
    nodes = WorkflowNodeRepository().fetch_all_by_workflow_id(workflow_id)
    return WorkflowResponseDTO.to_response(workflow, nodes)

Fixtures().add_test_data(1)
