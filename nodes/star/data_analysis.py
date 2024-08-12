from nodes.base_node import BaseNode, BaseNodeInput, InputType, NodeType
from services import GeminiService


class DataAnalysisNode(BaseNode):
    def __init__(self, **kwargs):
        if kwargs:
            super().__init__(**kwargs)
        else:
            inputs = [
                BaseNodeInput("data", InputType.COMMON, "text", is_required=True),
                BaseNodeInput("prompt", InputType.INTERNAL_ONLY, "prompt"),
            ]
            super().__init__(
                id='data_analysis',
                name="Data Analysis",
                icon_url="https://cdn-icons-png.flaticon.com/512/2921/2921914.png",
                description="Make sense of your data using Gemini Magic",
                node_type=NodeType.STAR.value,
                is_active=True,
                inputs=inputs,
                outputs=["response"],
                **kwargs
            )

    async def execute(self, input: dict) -> []:
        data = input.get("data")
        prompt = input.get("prompt")
        service = GeminiService()

        PROMPT = """
                You are an expert data analyst. Your. job is to analyse a blob of data and find meaning in it.
        Do understand these meanings, you decide you need to do some analysis.
        You always try to make sense of the data and then decide what should be shown to the user to help them understand their data and take some actions based on it.
        
        1. Determine the analysis to be done.
        2. Understand the visual components to be used for the analysis. Think about what data should be best represented in what visual component.
        3. Extract the data in the required format for every visual component.
        4. You can use the same data for multiple visual components or same visual component can have multiple data.
        5. Label the data in some way so that I understand what data it is. Also add a description to be shown to the user. Make it easily understandable to a non technical user.
        6. Also return a usage key, which tells the user how they can think about this data to improve their use case
        
        You are also given a user prompt which might tell you what the user is looking for in the data.
        Prioritize the data based on the prompt. If prompt is not given, you can use the data as is.
        
        Visual Components:
           1. one_line_graph
              * Simple one line graph with data points.
              * Return a nested dictionary with keys x and y. x is the x axis data and y is the y axis data. Both x and y
              contain an array of data points.
              * Also add keys label description and usage_key. Label is the name of the data,
               description is the description of the data and usage_key is how the user can use this data.
               Make this data human readable which a non technical user can understand.
              
        
        User Prompt:
        {prompt}
        
        
        Data:
        \\\
        {data}
        \\\
        
        Output Format:
        Return a JSON list of dictionaries, with each dictionary containing the 
        visual component id and the data required for that component.
        Keep the first key of dict as response, and the value as list of dictionaries.
        """

        formatted_prompt = PROMPT.format(data=data, prompt=prompt)
        response = await service.generate_cached_json_response(formatted_prompt, name=self.name, stream=False, img=False)
        # response is a json containing the visual components and the data required for each component
        # convert the json to a list of dictionaries
        res_list = response.get("response", [])
        return [
            {"response": res_list}
        ]