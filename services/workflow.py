from databases.repository.workflow import WorkflowRepository
from databases.repository.workflow_node import WorkflowNodeRepository
from databases.repository.workflow_run import WorkflowRunRepository
from databases.models.workflow_run import WorkflowRun
import datetime
from typing import Dict, List

from databases.models.workflow_schema import WorkflowSchema
from databases.models.workflow_node import WorkFlowNode

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

    async def update_workflow_post_execution(self, workflow_id, nodes: List[str], edges):
        workflow = self.workflow_repo.fetch_by_id(workflow_id)
        workflow.set_edges(edges)
        workflow.set_nodes(nodes)
        workflow.id = workflow_id
        self.workflow_repo.add_or_update(workflow)

    async def update_nodes_post_execution(self, workflow_id, updated_nodes):
        updated_node_ids = [node.id for node in updated_nodes]
        original_nodes = self.workflow_node_repo.fetch_all_by_workflow_id(workflow_id)

        # Update or create new nodes
        for node in updated_nodes:
            node.workflow = workflow_id
            # Remove all keys from node.available_inputs that contain input in the key
            node.available_inputs = {k: v for k, v in node.available_inputs.items() if "input" not in k}
            self.workflow_node_repo.add_or_update(node.id, node.to_dict())

        # Soft delete nodes that are not in the updated list
        for node in original_nodes:
            if node.id not in updated_node_ids:
                node.is_deleted = True
                node.workflow = None
                self.workflow_node_repo.add_or_update(node.id, node.to_dict())

    async def add_node_to_workflow_run(self, run: WorkflowRun, node: [WorkFlowNode]):
        run.nodes.append(node.to_dict())
        self.workflow_run_repo.add_or_update(run)

    async def initiate_workflow_run(self, workflow_id: str, run_id: str, num_nodes: int) -> WorkflowRun:
        started_at = datetime.datetime.now().timestamp() * 1000
        workflow_run = WorkflowRun(
            id=run_id,
            workflow_id=workflow_id,
            started_at=started_at,
            num_nodes=num_nodes,
            status="running"
        )
        self.workflow_run_repo.add_or_update(workflow_run)
        return workflow_run

    async def update_workflow_run(self, run: WorkflowRun, nodes: List[WorkFlowNode], edges: List[Dict[str, str]], executed_at: float):
        run.nodes = nodes
        run.edges = edges
        run.status = "completed"
        run.executed_at = executed_at
        self.workflow_run_repo.add_or_update(run)

    async def mark_workflow_run_failed(self, run: WorkflowRun):
        run.status = "failed"
        self.workflow_run_repo.add_or_update(run)


class WorkflowExecutorService:
    workflow_id = WorkflowSchema
    node_mapping: Dict[str, WorkFlowNode] = {}  # Store mapping of node id to node object
    adj_list: Dict[str, List[Dict[str, str]]] = {}  # Store adjacency list with handles
    input_edges: List[Dict[str, str]] = []
    execution_order = []
    workflow_service = WorkflowService()
    parent_node_map: Dict[str, List] = {}
    run= None

    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.execution_order = []
        self.node_mapping = {}
        self.adj_list = {}
        self.input_edges = []
        self.parent_node_map = {}
        self.run = None

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
            if target in self.parent_node_map.keys():
                self.parent_node_map[target].append(source)
            else:
                self.parent_node_map[target] = [source]

        self.adj_list = adj_list

    def all_parents_executed(self, node_id: str, visited: set):
        """ Returns True if all parent nodes of node are already executed else returns False """

        for parent_node in self.parent_node_map[node_id]:
            if parent_node not in visited:
                return False
        return True

    async def execute_node(self, node_id: str, visited: set, input_data: dict | None = None):
        """
        Execute a node and recursively execute its neighbors when all the inputs are available
        :param node_id: Node ID
        :param visited: Set of visited nodes
        :param input_data: Input data for the node [mostly coming from parent node]
        """

        if node_id not in visited:
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
            visited.add(node_id)

            for neighbor_info in self.adj_list.get(node_id, []):
                target_node_id = neighbor_info['target']
                input_handle = neighbor_info['inputHandle']
                output_handle = neighbor_info.get('outputHandle')
                handle_outputs = []
                for output in outputs:
                    if output_handle in output.keys():
                        handle_outputs.append(output[output_handle])

                # Recursively gather inputs for each neighboring node
                await self.gather_and_execute_neighbor(target_node_id, visited, input_handle,
                                                       handle_outputs)

    async def gather_and_execute_neighbor(self, target_node_id: str, visited: set, input_handle: str,
                                          handle_outputs: any):
        """
        Gather inputs for the neighboring node and execute it if all inputs are available
        """
        if target_node_id not in visited:
            target_node = self.node_mapping[target_node_id]
            target_node.available_inputs[input_handle] = handle_outputs
            can_execute = self.all_parents_executed(target_node_id, visited)
            if can_execute:
                try:
                    await self.execute_node(target_node_id, visited, target_node.available_inputs)
                except Exception as e:
                    await self.workflow_service.mark_workflow_run_failed(self.run)
                    raise e
            else:
                print(f"not now: {target_node.get_node().name}")

    async def execute(self, nodes: list, edges: list, run_id: str) -> WorkflowRun:
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
        self.node_mapping = {node.id: node for node in workflow_nodes}

        # Cleanup edges which have an invalid source or target
        valid_nodes = set(self.node_mapping.keys())
        self.input_edges = [edge for edge in edges if edge['source'] in valid_nodes and edge['target'] in valid_nodes]

        self._create_adjacency_list(workflow_nodes)

        visited = set()
        start_nodes = self.get_start_nodes()
        for start_node in start_nodes:
            await self.execute_node(start_node, visited)

        # Sort node mapping by execution order
        self.node_mapping = {node_id: self.node_mapping[node_id] for node_id in self.execution_order}

        # TODO: Do the following in a background task
        updated_nodes = list(self.node_mapping.values())
        updated_node_ids = [node.id for node in updated_nodes]
        await self.workflow_service.update_workflow_post_execution(self.workflow_id, updated_node_ids, edges)
        await self.workflow_service.update_nodes_post_execution(self.workflow_id, updated_nodes)
        executed_at = datetime.datetime.now().timestamp() * 1000
        await self.workflow_service.update_workflow_run(
            self.run,
            list(self.node_mapping.values()),
            edges,
            executed_at
        )

        return self.run
