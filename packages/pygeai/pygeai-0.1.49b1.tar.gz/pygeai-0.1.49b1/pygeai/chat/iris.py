from pygeai.chat.clients import ChatClient

llm_settings = {
    "temperature": 0.6,
    "max_tokens": 800,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.2
}


class Iris:
    def __init__(self):
        self.client = ChatClient()

    def stream_answer(self, messages):
        result = self.client.chat_completion(
            model="saia:agent:com.globant.iris",
            messages=messages,
            stream=True,
            **llm_settings
        )
        return result

