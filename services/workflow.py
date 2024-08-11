import uuid

from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.repository.workflow_run import WorkflowRunRepository
from databases.models.workflow_run import WorkflowRun
import datetime
from typing import Dict, List

from databases.models.workflow_schema import WorkflowSchema
from databases.models.workflow_node import WorkFlowNode
from services import GeminiService


# class Edge:
#     def __init__(self):
#         self.target
#         self.source
#         self.output_handler
#         self.input_handler
#
#     # add setters and getters


class WorkflowService:
    workflow_repo = WorkflowRepository()
    workflow_node_repo = WorkflowNodeRepository()
    workflow_run_repo = WorkflowRunRepository()

    def __init__(self):
        pass

    async def update_workflow_post_execution(self, workflow_id, nodes: List[str], edges, run_id: str, name=None):
        service = GeminiService()
        prompt = """
        You are given the data about a workflow. It is basically a graph of noded connected to each other using edges.
        Each node can have multiple input and output edges and can have multiple inputs and outputs.
        
        Workflow Name: {name}
        
        Workflow Nodes: {nodes}
        
        Workflow Edges: {edges}
        
        Your job is to write a 2 line summary of the workflow.
        The summary should explain to the user in a very simple way what the workflow does.
        Try to be witty in unique ways, but do not force the joke. Dont do the cliche its like templates.
        """
        prompt = prompt.format(name=name, nodes=str(nodes), edges=str(edges))
        workflow = self.workflow_repo.fetch_by_id(workflow_id)
        workflow.set_edges(edges)
        workflow.set_nodes(nodes)
        workflow.id = workflow_id
        workflow.latest_run_id = run_id

        response = await service.generate_cached_response(prompt, 'workflow', False) if workflow.ai_description is None else workflow.ai_description
        workflow.ai_description = response
        if name:
            workflow.name = name
        self.workflow_repo.add_or_update(workflow)

    async def update_workflow(self, workflow_id, nodes: List[str], edges, name=None):
        service = GeminiService()
        prompt = """
                You are given the data about a workflow. It is basically a graph of noded connected to each other using edges.
                Each node can have multiple input and output edges and can have multiple inputs and outputs.

                Workflow Name: {name}

                Workflow Nodes: {nodes}

                Workflow Edges: {edges}

                Your job is to write a 2 line summary of the workflow.
                The summary should explain to the user in a very simple way what the workflow does.
                Try to be witty in unique ways, but do not force the joke. Dont do the cliche its like templates.
                """
        prompt = prompt.format(name=name, nodes=str(nodes), edges=str(edges))
        workflow = self.workflow_repo.fetch_by_id(workflow_id)
        workflow.name = name
        workflow.set_edges(edges)
        workflow.set_nodes(nodes)

        response = await service.generate_cached_response(prompt, 'workflow', False) if workflow.ai_description is None else workflow.ai_description

        workflow.ai_description = response
        if name:
            workflow.name = name
        self.workflow_repo.add_or_update(workflow)

    async def create_workflow(self, name, description, owner):
        id = uuid.uuid4().hex
        workflow = WorkflowSchema(id=id, name=name, description=description, owner=owner)
        self.workflow_repo.add_or_update(workflow)
        return id

    async def fetch_workflow_node_by_id(self, node_id) -> WorkFlowNode:
        return self.workflow_node_repo.fetch_by_id(node_id)

    async def get_original_workflow_nodes(self, workflow_id):
        return self.workflow_node_repo.fetch_all_by_workflow_id(workflow_id)

    async def update_nodes_post_execution(self, workflow_id, updated_nodes, workflow_node_ids):
        original_nodes = self.workflow_node_repo.fetch_all_by_workflow_id(workflow_id)

        # Update or create new nodes
        for node in updated_nodes:
            node.workflow = workflow_id
            # Remove all keys from node.available_inputs that contain input in the key
            node.available_inputs = {k: v for k, v in node.available_inputs.items()}
            self.workflow_node_repo.add_or_update(node.id, node.to_dict())

        # Soft delete nodes that are not in the updated list
        for node in original_nodes:
            # Not using updated_nodes as it is possible that other nodes have not yet executed and something failed
            # D not delete those
            if node.id not in workflow_node_ids:
                node.is_deleted = True
                node.workflow = None
                self.workflow_node_repo.add_or_update(node.id, node.to_dict())

    async def add_node_to_workflow_run(self, run: WorkflowRun, node: [WorkFlowNode]):
        run.nodes.append(node.to_dict())
        self.workflow_run_repo.add_or_update(run)

    async def initiate_workflow_run(self, workflow_id: str, run_id: str, num_nodes: int) -> WorkflowRun:
        try:
            run = self.workflow_run_repo.get(run_id)
        except Exception as e:
            run = None
        started_at = datetime.datetime.now().timestamp() * 1000
        workflow_run = WorkflowRun(
            id=run_id,
            workflow_id=workflow_id,
            started_at=started_at,
            num_nodes=num_nodes,
            status="RUNNING" if not run else run.status
        )
        self.workflow_run_repo.add_or_update(workflow_run)
        return workflow_run

    async def update_workflow_run(self, run: WorkflowRun, nodes: List[WorkFlowNode], edges: List[Dict[str, str]],
                                  executed_at: float):
        run.nodes = nodes
        run.edges = edges
        run.mark_success()
        run.executed_at = executed_at
        self.workflow_run_repo.add_or_update(run)

    async def mark_workflow_run_failed(self, run: WorkflowRun):
        run.mark_failed()
        self.workflow_run_repo.add_or_update(run)

    async def mark_workflow_run_waiting_for_approval(self, run: WorkflowRun, nodeId: str):
        run.mark_waiting_for_approval()
        run.approve_node = nodeId
        self.workflow_run_repo.add_or_update(run)



class WorkflowExecutorService:
    workflow_id = WorkflowSchema
    node_mapping: Dict[str, WorkFlowNode] = {}  # Store mapping of node id to node object
    adj_list: Dict[str, List[Dict[str, str]]] = {}  # Store adjacency list with handles
    input_edges: List[Dict[str, str]] = []
    execution_order = []
    workflow_service = WorkflowService()
    run = None
    is_approval_flow = False
    is_human_approval_required = False

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.execution_order = []
        self.node_mapping = {}
        self.adj_list = {}
        self.input_edges = []
        self.run = None
        self.is_approval_flow = False
        self.is_human_approval_required = False

    def get_start_nodes(self) -> List[str]:
        all_nodes = set(self.adj_list.keys())
        target_nodes = set([edge['target'] for edge in self.input_edges])
        start_nodes = all_nodes - target_nodes
        return list(start_nodes)

    def _create_adjacency_list(self, workflow_nodes: List[WorkFlowNode]):
        adj_list = {node.id: [] for node in workflow_nodes}
        for edge in self.input_edges:
            source = edge['source']
            target = edge['target']
            output_handle = edge.get('outputHandle', "response") or "response"
            input_handle = edge.get('inputHandle', None)

            if source not in adj_list:
                adj_list[source] = []

            adj_list[source].append({'target': target, 'outputHandle': output_handle, "inputHandle": input_handle})

        self.adj_list = adj_list

    def all_edges_executed(self, node_id: str, visited: set):
        """
        Returns if all the input edges of a node are executed
        """
        input_edges = [edge for edge in self.input_edges if edge['target'] == node_id]
        for edge in input_edges:
            handle_key = f"{edge["inputHandle"]}-{edge["outputHandle"]}"
            if handle_key not in visited:
                return False
        return True

    async def execute_node(self, node_id: str, visited: set, input_data: dict | None = None):
        """
        Execute a node and recursively execute its neighbors when all the inputs are available
        :param node_id: Node ID
        :param visited: Set of visited nodes
        :param input_data: Input data for the node [mostly coming from parent node]
        """

        if node_id not in visited and self.is_human_approval_required is False:
            # Get the current node
            node: WorkFlowNode = self.node_mapping[node_id]
            base_node = node.get_node()
            available_inputs = node.available_inputs

            if input_data:
                available_inputs.update(input_data)

            outputs = await base_node.execute(available_inputs)
            if isinstance(outputs, dict):
                outputs = [outputs]

            node.outputs = outputs
            node.available_inputs = available_inputs
            # TODO: Make this async
            await self.workflow_service.add_node_to_workflow_run(run=self.run, node=node)
            self.execution_order.append(node_id)

            if not self.is_approval_flow and base_node.id == "human_approval":
                await self.workflow_service.mark_workflow_run_waiting_for_approval(self.run, node.id)
                self.is_human_approval_required = True
                return

            for neighbor_info in self.adj_list.get(node_id, []):
                print(f"Parent {node_id} -> Child {neighbor_info['target']}")
                target_node_id = neighbor_info['target']
                input_handle = neighbor_info['inputHandle']
                output_handle = neighbor_info.get('outputHandle')
                handle_outputs = []
                for output in outputs:
                    if output_handle in output.keys():
                        handle_outputs.append(output[output_handle])

                # Recursively gather inputs for each neighboring node
                await self.gather_and_execute_neighbor(target_node_id, visited, input_handle, output_handle,
                                                       handle_outputs)

    async def gather_and_execute_neighbor(self, target_node_id: str, visited: set, input_handle: str,
                                          output_handle: str,
                                          handle_outputs: any):
        """
        Gather inputs for the neighboring node and execute it if all inputs are available
        """
        handle_key = f"{input_handle}-{output_handle}"
        print("Gathering inputs for ", target_node_id, (handle_key not in visited), input_handle, output_handle)
        if handle_key not in visited:
            target_node = self.node_mapping[target_node_id]
            target_node.available_inputs[input_handle] = handle_outputs
            print("Available Inputs : ", {target_node.node}, " ", target_node.available_inputs.keys())
            visited.add(handle_key)

            can_execute = self.all_edges_executed(target_node_id, visited)
            if can_execute:
                try:
                    await self.execute_node(target_node_id, visited, target_node.available_inputs)
                except Exception as e:
                    print(f"Error executing node {target_node.get_node().name} {e}")
                    await self.workflow_service.mark_workflow_run_failed(self.run)
                    raise e
            else:
                print(f"not now: {target_node.get_node().name}")

    async def execute(self, nodes: list, edges: list, run_id: str, orign_node_id: str | None) -> WorkflowRun:
        """
        DFS traversal of the workflow graph
        @param nodes: List of nodes from frontend.
        @param edges: List of edges from frontend.
        A lot of the data is already present in the workflow object but we need to update the available inputs
        Thus might as well pass the nodes from the frontend
        :return:
        """
        self.run = await self.workflow_service.initiate_workflow_run(self.workflow_id, run_id, num_nodes=len(nodes))

        workflow_nodes = [WorkFlowNode(**node) for node in nodes]

        origin_node = [node for node in workflow_nodes if node.id == orign_node_id][0] if orign_node_id else None
        if origin_node:
            origin_node_prev_version = await self.workflow_service.fetch_workflow_node_by_id(orign_node_id)
            origin_node.available_inputs = origin_node_prev_version.available_inputs
            if origin_node.node == "human_approval":
                origin_node.available_inputs["is_approved"] = True
                self.is_approval_flow = True

            # Append origin node to workflow_nodes, replace the existing node
            workflow_nodes = [node for node in workflow_nodes if node.id != orign_node_id]
            workflow_nodes.append(origin_node)

        self.node_mapping = {node.id: node for node in workflow_nodes}

        # Cleanup edges which have an invalid source or target
        valid_nodes = set(self.node_mapping.keys())
        self.input_edges = [edge for edge in edges if edge['source'] in valid_nodes and edge['target'] in valid_nodes]

        self._create_adjacency_list(workflow_nodes)

        workflow_node_ids = [node.id for node in workflow_nodes]

        visited = set()
        start_nodes = self.get_start_nodes() if not orign_node_id else [orign_node_id]
        for start_node in start_nodes:
            await self.execute_node(start_node, visited)

        # Sort node mapping by execution order
        self.node_mapping = {node_id: self.node_mapping[node_id] for node_id in self.execution_order}
        for node in workflow_nodes:
            if node.id in self.node_mapping:
                workflow_nodes[workflow_nodes.index(node)] = self.node_mapping[node.id]

        # TODO: Do the following in a background task

        await self.workflow_service.update_workflow_post_execution(self.workflow_id, workflow_node_ids, edges, run_id)
        await self.workflow_service.update_nodes_post_execution(self.workflow_id, workflow_nodes, workflow_node_ids)
        executed_at = datetime.datetime.now().timestamp() * 1000
        if not self.is_human_approval_required:
            await self.workflow_service.update_workflow_run(
                self.run,
                workflow_nodes,
                edges,
                executed_at
            )

        return self.run
