import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from dotenv import load_dotenv

from databases.fixtures import Fixtures
from databases.repository.node import NodeRepository
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.repository.workflow_run import WorkflowRunRepository
from services.utils import format_input_edges
from services.workflow import WorkflowExecutorService
from workflows.base_workflow_dto import WorkflowResponseDTO
import google.generativeai as genai

app = FastAPI()

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
genai.configure(api_key=GEMINI_API_KEY)

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
    edges: list | None = None


@app.post("/workflow/run")
async def run_workflow(request: WorkflowRunRequest):
    """
    Run a workflow
    :param request: WorkflowRunRequest
    :return:  Response

    This currently only supports serial execution of the workflow
    """
    workflow_id = request.id

    formatted_edges = format_input_edges(request.edges)

    workflow_executor_service = WorkflowExecutorService(workflow_id=workflow_id)
    # Workflow is executed and the mapping of node_id to node is returned
    mapping = await workflow_executor_service.execute(request.nodes, formatted_edges)

    response = []
    for node_id, node in mapping.items():
        response.append({
            "id": node_id,
            "key": node.node,
            "output": node.outputs
        })
    return response


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


@app.get("/base-nodes")
async def get_nodes():
    nodes = NodeRepository().fetch_all()
    return nodes


@app.get("/workflow/{workflow_id}/runs")
async def get_workflow_runs(workflow_id: str):
    """
    Get all runs for a workflow
    :param workflow_id: str
    :return:  Response
    """
    workflow_runs = WorkflowRunRepository().fetch_by_workflow_id(workflow_id)
    return workflow_runs