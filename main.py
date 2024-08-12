import asyncio
import datetime
import json
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

from databases.fixtures import Fixtures
from databases.repository.google_user import GoogleUserRepository
from databases.repository.node import NodeRepository
from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.repository.workflow_run import WorkflowRunRepository
from services.utils import format_input_edges
from api_serializer.base_workflow_dto import WorkflowResponseDTO, WorkflowRunRequest
import google.generativeai as genai
from services.workflow import WorkflowExecutorService, WorkflowService

app = FastAPI()

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)
genai.configure(api_key=GEMINI_API_KEY)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

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
    node_id = request.node_id

    formatted_edges = format_input_edges(request.edges)

    workflow_executor_service = WorkflowExecutorService(workflow_id=workflow_id)
    # Workflow is executed and the mapping of node_id to node is returned
    run = await workflow_executor_service.execute(request.nodes, formatted_edges, request.run_id, orign_node_id=node_id)
    return run


@app.get("/workflows/{owner}")
async def get_workflows(owner: str):
    """
    Get all workflows
    :return:  Response
    """
    workflows = WorkflowRepository().fetch_all(owner or 'admin')
    formatted_workflows = []
    for workflow in workflows:
        nodes = WorkflowNodeRepository().fetch_all_by_workflow_id(workflow.id)
        try:
            run = WorkflowRunRepository().get(workflow.latest_run_id)
        except Exception:
            run = None
        formatted_workflows.append(WorkflowResponseDTO.to_response(workflow, nodes, run))
    return formatted_workflows


@app.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    """
    Get a workflow
    :param workflow_id: str
    :return:  Response
    """
    workflow = WorkflowRepository().fetch_by_id(workflow_id)
    nodes = WorkflowNodeRepository().fetch_all_by_workflow_id(workflow_id)
    try:
        run = WorkflowRunRepository().get(workflow.latest_run_id)
    except Exception:
        run = None
    return WorkflowResponseDTO.to_response(workflow, nodes, run)


@app.put("/workflow")
async def update_workflow(request: WorkflowResponseDTO):
    """
    Update a workflow
    :param request: WorkflowResponseDTO
    :return:  Response
    """
    workflow_service = WorkflowService()
    payload = request.to_dict()
    workflow_id = payload.get("id")
    name = payload.get("name")
    updated_node_ids = [node.id for node in payload.get("nodes")]
    try:
        await workflow_service.update_workflow(workflow_id, updated_node_ids, payload['edges'], name)
        await workflow_service.update_nodes_post_execution(workflow_id, payload["nodes"], updated_node_ids)
        return {"success": True, "error": None}
    except Exception as e:
        print(f"Error in updating workflow: {e}")
        return {"success": False, "error": str(e)}


@app.post("/workflow")
async def create_workflow(request: WorkflowResponseDTO):
    """
    Create a workflow
    :param request: WorkflowResponseDTO
    :return:  Response
    """
    workflow_service = WorkflowService()
    payload = request.to_dict()
    name = payload.get("name") or 'New Workflow'
    owner = payload.get("owner")
    try:
        workflow_id = await workflow_service.create_workflow(name, '', owner)
        return {"success": True, "error": None, "workflow_id": workflow_id}
    except Exception as e:
        print(f"Error in creating workflow: {e}")
        return {"success": False, "error": str(e)}


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


# Webhooks

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
            if data.status != "RUNNING":
                print("Closing as status is ", data.status)
                await websocket.close()
                break

            data_json = json.dumps(data.to_dict())
            await manager.broadcast(data_json)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"websocket error: {e}")


# Authentication
from google_auth_oauthlib.flow import Flow
from dataclasses import dataclass
from googleapiclient.discovery import build


@dataclass
class GoogleAuthRequest:
    token: str


@dataclass
class GoogleAuthResponse:
    is_successful: bool
    email: str
    name: str
    message: str
    photo_url: str = None


def create_flow():
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',  # Path to your OAuth2 credentials
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/drive'
        ],  # Adjust scopes based on your needs
        redirect_uri='postmessage',
    )
    return flow


@app.post("/google-auth")
async def signup(request: GoogleAuthRequest):
    token = request.token
    flow = create_flow()
    flow.fetch_token(code=token)
    credentials = flow.credentials
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info.get('email')
    name = user_info.get('name')
    photoUrl = user_info.get('photoUrl')

    google_user_repo = GoogleUserRepository()
    try:
        existing_user = google_user_repo.get(email)
    except Exception:
        existing_user = None

    if existing_user:
        return GoogleAuthResponse(is_successful=False, email=email, name=name, message="User already exists")
    data = {
        "email": email,
        "name": name,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
        "code": token,
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "photoUrl": photoUrl
    }
    google_user_repo.add_or_update(email, data)
    return GoogleAuthResponse(is_successful=True, email=email, name=name, message="User created", photo_url=photoUrl)


@app.post("/login")
async def login(token: str):
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Get user info
        userid = idinfo['sub']
        email = idinfo['email']
        return {"message": "Login successful", "user_id": userid, "email": email}
    except ValueError:
        print("Invalid token")
        raise Exception("Invalid token")
