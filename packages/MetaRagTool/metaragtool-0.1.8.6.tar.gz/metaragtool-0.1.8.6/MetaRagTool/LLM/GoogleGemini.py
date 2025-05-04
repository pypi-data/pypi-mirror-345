import weave
from MetaRagTool.LLM.LLMIdentity import LLMIdentity
from google import genai
from google.genai import types
from MetaRagTool import Constants


class Gemini(LLMIdentity):

    GEMINI_PRO = 'gemini-pro'
    GEMINI_2_PRO='gemini-2.5-pro-preview-03-25' # RPM = 5
    GEMINI_2_FLASH_THINK='gemini-2.0-flash-thinking-exp-01-21' # RPM = 10
    GEMINI_2_FLASH = 'gemini-2.0-flash' # RPM = 15
    GEMINI_2_FLASH_LIGHT="gemini-2.0-flash-lite"  # RPM = 30
    GEMINI_2P5_FLASH="gemini-2.5-flash-preview-04-17" # RPM = 10

    def __init__(self, model_name=GEMINI_2_FLASH, has_memory=True,custom_system_message=None,RequestPerMinute_limit=15):
        super().__init__(model_name,has_memory=has_memory,custom_system_message=custom_system_message,RequestPerMinute_limit=RequestPerMinute_limit)
        self.client = genai.Client(api_key=Constants.API_KEY_GEMINI)




    @weave.op()
    def generate(self, prompt: str, query_to_be_saved: str = None, tool_function=None) -> str:
        # print(prompt)
        if self.RequestPerMinute_limit > 0:
            self.manage_rpm()
        try:
            if query_to_be_saved is None:
                query_to_be_saved = prompt

            if self.custom_system_message is not None: system_instruction = self.custom_system_message
            else: system_instruction = self.systemMessage_tooluse if tool_function is not None else self.systemMessage

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
            )
            if tool_function is not None:
                config.tools=[tool_function]
                # config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)

            self.chat = self.client.chats.create(model=self.model_name,
                                                 config=config,
                                                 history=self.messages_history
                                                 )

            response = self.chat.send_message(message=prompt)


            self.messages_history = self.chat.get_history()

            if tool_function is None:
                self.messages_history[-2].parts[0].text = query_to_be_saved

            if not self.has_memory:
                self.messages_history = []

            return response.text

        except Exception as e:
            return f"Error generating response: {str(e)}"

