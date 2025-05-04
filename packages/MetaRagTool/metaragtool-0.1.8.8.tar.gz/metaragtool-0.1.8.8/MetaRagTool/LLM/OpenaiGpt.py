from MetaRagTool.LLM.LLMIdentity import LLMIdentity
from openai import OpenAI

from MetaRagTool import Constants

endpoint = "https://models.inference.ai.azure.com"






class OpenaiGpt(LLMIdentity):

    def __init__(self, model="gpt-4o"):
        super().__init__(model_name=model)
        self.client = OpenAI(
            base_url=endpoint,
            api_key=Constants.API_KEY_OPENAI,
        )

    def setSystemMessage(self, systemMessage):
        self.systemMessage = systemMessage



    def add_to_history(self, message, role:LLMIdentity.MessageRole):
        pass


    def generate(self, prompt: str,query_to_be_saved: str=None,tool_function=None) -> str:
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.systemMessage},
                {"role": "user", "content": prompt}
            ],
            model=self.model_name
        )
        return response.choices[0].message.content

    def generate_with_tools (self, messages, tools):
        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            tools=tools
        )
        return response