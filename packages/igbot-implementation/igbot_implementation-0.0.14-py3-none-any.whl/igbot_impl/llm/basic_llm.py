from igbot_base.llm import Llm
from igbot_base.llmmemory import LlmMemory
from igbot_base.models import Model
from igbot_base.response_formats import ResponseFormat


class BasicLlm(Llm):

    def __init__(self,
                 name: str,
                 model: Model,
                 temperature: float,
                 response_format: ResponseFormat = None):
        super().__init__(name, model, temperature, response_format)
        self.__model = model.value.get_name()
        self.__client = model.value.get_client()

    def _call(self, user_query: str, history: LlmMemory, params: dict) -> str:
        history.append_user(user_query)
        messages = history.retrieve()
        response = self.__client.chat.completions.create(
            model=self.__model,
            messages=messages,
            **super().get_additional_llm_args()
        )
        llm_response = response.choices[0].message.content
        history.append_assistant(llm_response)

        return llm_response
