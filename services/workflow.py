from typing import Dict, List

from databases.repository.workflow_node import WorkflowNodeRepository
from workflows.base_workflow import WorkflowSchema
from workflows.workflow_node import WorkFlowNode


class WorkflowService:
    workflow = WorkflowSchema
    node_mapping: Dict[str, WorkFlowNode] = {}  # Store mapping of node id to node object
    adj_list: Dict[str, List[Dict[str, str]]] = {}  # Store adjacency list with handles

    def __init__(self, workflow: WorkflowSchema):
        self.workflow = workflow

    def get_start_nodes(self) -> List[str]:
        all_nodes = set(self.adj_list.keys())
        target_nodes = set()

        for edge in self.workflow.edges:
            target_nodes.add(edge['target'])

        start_nodes = all_nodes - target_nodes
        return list(start_nodes)

    def _create_adjacency_list(self, workflow_nodes: List[WorkFlowNode]):
        adj_list = {node.id: [] for node in workflow_nodes}
        for edge in self.workflow.edges:
            source = edge['source']
            target = edge['target']
            output_handle = edge.get('outputHandle', "response")
            input_handle = edge.get('inputHandle', None)

            if source not in adj_list:
                adj_list[source] = []

            adj_list[source].append({'target': target, 'outputHandle': output_handle, "inputHandle": input_handle})

        self.adj_list = adj_list

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

            print(f"Executing node: {base_node.name} for {self.workflow.name}")
            print(f"Inputs: {available_inputs}")

            # Execute the current node and mark it as visited
            outputs = await base_node.execute(available_inputs)
            print(f"outputs: {outputs}")
            visited.add(node_id)

            for neighbor_info in self.adj_list.get(node_id, []):
                print(f"Neighbor: {neighbor_info}")
                target_node_id = neighbor_info['target']
                input_handle = neighbor_info['inputHandle']
                output_handle = neighbor_info.get('outputHandle')
                print(f"Target Node: {target_node_id} - Input Handle: {input_handle} - Output Handle: {output_handle}")

                # Recursively gather inputs for each neighboring node
                await self.gather_and_execute_neighbor(target_node_id, visited, input_handle,
                                                       outputs.get(output_handle))

    async def gather_and_execute_neighbor(self, target_node_id: str, visited: set, input_handle: str, edge_output: any):
        """
        Gather inputs for the neighboring node and execute it if all inputs are available
        """
        if target_node_id not in visited:
            target_node = self.node_mapping[target_node_id]
            target_available_inputs = target_node.available_inputs
            target_available_inputs[input_handle] = edge_output

            can_execute = target_node.can_execute()
            print("can execute:", target_node.get_node().name, can_execute, target_available_inputs)

            if can_execute:
                await self.execute_node(target_node_id, visited, target_available_inputs)

    async def execute(self):
        """
        DFS traversal of the workflow graph
        :return:
        """
        repo = WorkflowNodeRepository()
        workflow_nodes = repo.fetch_all_by_workflow_id(self.workflow.id)
        self.node_mapping = {node.id: node for node in workflow_nodes}

        self._create_adjacency_list(workflow_nodes)
        print("Adjacency List:", self.adj_list)

        visited = set()
        start_nodes = self.get_start_nodes()
        for start_node in start_nodes:
            await self.execute_node(start_node, visited)

