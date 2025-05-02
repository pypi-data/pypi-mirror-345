import warnings
from typing import List, Union, Dict

from openai import OpenAI, Stream
from openai.types import Embedding
from openai.types.chat import ChatCompletionChunk
from pydantic import BaseModel

from adprompt.rerank import RerankScore


class OpenAIConfig(BaseModel):
    base_url: str
    api_key: str
    model: str = None
    client_id: str = None


class AIClient:

    def __init__(self, openai_config: Union[OpenAIConfig, List[OpenAIConfig]]):
        self.client_map: Dict[str, OpenAI] = {}
        self.client_default_model: Dict[str, str] = {}

        if not isinstance(openai_config, list):
            arr = [openai_config]
        else:
            arr = openai_config
        for i in arr:
            client = OpenAI(
                api_key=i.api_key,
                base_url=i.base_url,
            )
            client_id = i.client_id or 'default'
            default_model = i.model
            self.client_map[client_id] = client
            self.client_default_model[client_id] = default_model

    def chat(
            self,
            messages: List[dict],
            client_id: str = None,
            temperature: float = 0.6,
            **kwargs,
    ) -> str:
        if kwargs.get('stream'):
            warnings.warn('use "stream_chat" instead')
            kwargs.pop('stream')

        if 'model' not in kwargs:
            kwargs['model'] = self._select_default_model(client_id)
        client = self._select_client(client_id)
        completion = client.chat.completions.create(
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return completion.choices[0].message.content

    def stream_chat(
            self,
            messages: List[dict],
            client_id: str = None,
            temperature: float = 0.6,
            **kwargs,
    ) -> Stream[ChatCompletionChunk]:
        if 'stream' not in kwargs:
            kwargs['stream'] = True
        if 'model' not in kwargs:
            kwargs['model'] = self._select_default_model(client_id)
        client = self._select_client(client_id)
        completion = client.chat.completions.create(
            messages=messages,
            temperature=temperature,
            **kwargs,
        )
        return completion

    def _select_client(self, client_id: str = None) -> OpenAI:
        if client_id is None:
            return self.client_map['default']
        return self.client_map[client_id]

    def _select_default_model(self, client_id: str = None) -> str:
        if client_id is None:
            return self.client_default_model['default']
        return self.client_default_model[client_id]

    def embed(
            self,
            input: List[str],
            client_id: str = None,
            **kwargs,
    ) -> List[Embedding]:
        if 'model' not in kwargs:
            kwargs['model'] = self._select_default_model(client_id)
        client = self._select_client(client_id)
        resp = client.embeddings.create(
            input=input,
            **kwargs,
        ).data
        return resp

    def rerank(
            self,
            query: str,
            text: List[str],
            client_id: str = None,
            model: str = None,
    ) -> List[RerankScore]:
        if model is None:
            model = self._select_default_model(client_id)
        client = self._select_client(client_id)
        resp = client.post(
            'score',
            cast_to=Dict,
            body=dict(
                model=model,
                text_1=query,
                text_2=text,
            )
        )
        result = [RerankScore(**i) for i in resp['data']]
        return result
