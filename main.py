import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from dotenv import load_dotenv

from databases.fixtures import Fixtures
from databases.repository.node import NodeRepository
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from services.workflow import WorkflowService
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
    nodes = request.nodes
    edges = request.edges

    formatted_edges = []
    for edge in edges:
        edge_output = {
            **edge,
            "outputHandle": edge.get('sourceHandle', "response"),
            "inputHandle": edge.get('targetHandle', None)
        }
        # Remove all keys that are not string or are not required
        edge_output.pop('sourceHandle', None)
        edge_output.pop('targetHandle', None)
        edge_output = {k: v for k, v in edge_output.items() if isinstance(v, str)}

        formatted_edges.append(edge_output)

    workflow = WorkflowRepository().fetch_by_id(workflow_id)
    workflow_service = WorkflowService(workflow=workflow)
    mapping = await workflow_service.execute(nodes, formatted_edges)

    # Update the workflow with the new nodes and edges
    workflow_repo = WorkflowRepository()
    node_repo = WorkflowNodeRepository()

    original_nodes = WorkflowNodeRepository().fetch_all_by_workflow_id(workflow_id)
    updated_nodes = list(mapping.values())
    updated_node_ids = [node.id for node in updated_nodes]

    workflow.set_edges(formatted_edges)
    workflow.set_nodes(updated_node_ids)
    workflow_repo.add_or_update(workflow)

    for node in updated_nodes:
        node.workflow = workflow_id
        # Remove all keys from node.available_inputs that contain input in the key
        node.available_inputs = {k: v for k, v in node.available_inputs.items() if "input" not in k}
        node_repo.add_or_update(node.id, node.to_dict())

    for node in original_nodes:
        if node.id not in updated_node_ids:
            node_repo.delete(node.id)

    response = []
    for node_id, node in mapping.items():
        response.append({
            "id": node_id,
            "name": node.node,
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


@app.get("/nodes")
async def get_nodes():
    nodes = NodeRepository().fetch_all()
    return nodes
