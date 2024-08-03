import asyncio
import json
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from databases.fixtures import Fixtures
from databases.repository.node import NodeRepository
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.repository.workflow_run import WorkflowRunRepository
from services.utils import format_input_edges
from api_serializer.base_workflow_dto import WorkflowResponseDTO, WorkflowRunRequest
import google.generativeai as genai
from services.workflow import WorkflowExecutorService

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
    run = await workflow_executor_service.execute(request.nodes, formatted_edges, request.run_id)
    return run


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
async def get_base_nodes():
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


def get_workflow_nodes(workflow_id: str):
    """
    Get a node
    :param workflow_id: str
    :return:  Response
    """
    return WorkflowNodeRepository().fetch_all_by_workflow_id(workflow_id)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            if connection.application_state == WebSocketState.CONNECTED:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/result/{run_id}")
async def workflow_nodes_websocket(websocket: WebSocket, run_id: str):
    await manager.connect(websocket)
    total_not_found = 0
    try:
        while True:
            await asyncio.sleep(1)
            try:
                data = WorkflowRunRepository().get(run_id)
            except Exception:
                # Run not yet created or not at all found
                total_not_found += 1
                if total_not_found > 2:
                    print("Closing as not found")
                    await websocket.close()
                    break
                continue
            nodes = data.nodes
            if len(nodes) == data.num_nodes:
                print("Closing as all nodes found")
                await websocket.close()
                break
            if data.status in ["failed", "completed"]:
                print("Closing as status is ", data.status)
                await websocket.close()
                break

            data_json = json.dumps(data.to_dict())
            await manager.broadcast(data_json)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"websocket error: {e}")
