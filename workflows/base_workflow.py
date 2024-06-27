from typing import List, Optional, Dict
from pydantic import BaseModel

from databases.repository.workflow_node import WorkflowNodeRepository
from workflows.workflow_node import WorkFlowNode


def are_all_inputs_ready_for_node(node: WorkFlowNode):
    root_node = node.node
    for inputs in root_node.inputs:
        if inputs not in node.input.keys():
            return False
    return True


class WorkflowSchema(BaseModel):
    """This is the schema for a workflow. Created by user."""
    id: str
    name: str
    description: Optional[str] = None
    owner: str
    nodes: List[str] = {}  # Store individual nodes
    edges: List[Dict[str, str]] = []  # Store edges (source, target, sourceHandle)
    adj_list: Dict[str, List[Dict[str, str]]] = {}  # Store adjacency list with handles

    def __str__(self):
        return f"{self.name} - {self.description or 'No description'}"

    def add_nodes(self, nodes: List[WorkFlowNode]):
        for node in nodes:
            self.nodes.append(node.id)

    def add_edges(self, edges: List[Dict[str, str]]):
        self.edges = edges or []

    # def get_node(self, id: str) -> Optional[WorkFlowNode]:
    #     return self.nodes.get(id)

    def get_start_nodes(self) -> List[str]:
        all_nodes = set(self.adj_list.keys())
        target_nodes = set()

        for edge in self.edges:
            target_nodes.add(edge['target'])

        start_nodes = all_nodes - target_nodes
        return list(start_nodes)

    def _create_adjacency_list(self, workflow_nodes: List[WorkFlowNode]):
        adj_list = {node_id: [] for node_id in workflow_nodes}
        for edge in self.edges:
            source = edge['source']
            target = edge['target']
            output_handle = edge.get('outputHandle', "response")
            input_handle = edge.get('inputHandle', None)

            if source not in adj_list:
                adj_list[source] = []

            adj_list[source].append({'target': target, 'outputHandle': output_handle, "inputHandle": input_handle})

        self.adj_list = adj_list

    async def execute_node(self, node_id: str, visited: set, input_data: dict | None = None):
        if node_id not in visited:
            # Get the current node
            workflow_node = self.get_node(node_id)
            inputs = workflow_node.input  # Assuming WorkFlowNode has an input property

            # Update the inputs with the input_data if any
            if input_data:
                inputs.update(input_data)

            root_node = workflow_node.node  # Assuming WorkFlowNode has a node property
            print(f"Executing node: {node_id}")
            print(f"Inputs: {inputs}")

            # Execute the current node and mark it as visited
            outputs = await root_node.execute(inputs)
            print(f"Outputs: {outputs}")
            visited.add(node_id)

            # Prepare inputs for neighboring nodes
            for neighbor_info in self.adj_list.get(node_id, []):
                print(f"Neighbor: {neighbor_info}")
                target_node_id = neighbor_info['target']
                input_handle = neighbor_info['inputHandle']
                output_handle = neighbor_info.get('outputHandle')
                print(f"Target Node: {target_node_id} - Input Handle: {input_handle} - Output Handle: {output_handle}")

                # Recursively gather inputs for each neighboring node
                await self.gather_and_execute_neighbor(target_node_id, visited, input_handle,
                                                       outputs.get(output_handle))

    async def gather_and_execute_neighbor(self, node_id: str, visited: set, input_handle: str, edge_output: any):
        # Get or create the input storage for the neighbor node
        print("Processing: ", node_id in visited, "", edge_output)
        if node_id not in visited:
            target_node = self.get_node(node_id)
            target_node.input[input_handle] = edge_output

            if target_node.node.can_execute(target_node.input):
                await self.execute_node(node_id, visited, target_node.input)

    async def execute(self):
        """
        DFS traversal of the workflow graph
        :return:
        """
        repo = WorkflowNodeRepository()
        workflow_nodes = repo.fetch_workflow_nodes_by_workflow_id(self.id)
        self._create_adjacency_list(workflow_nodes)
        print("Adjacency List:", self.adj_list)
        visited = set()
        start_nodes = self.get_start_nodes()
        for start_node in start_nodes:
                await self.execute_node(start_node, visited)

    def to_dict(self) -> dict:
        return self.__dict__
