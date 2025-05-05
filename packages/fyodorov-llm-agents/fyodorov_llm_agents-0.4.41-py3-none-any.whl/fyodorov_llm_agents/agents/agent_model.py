import os
import re
from pydantic import BaseModel, HttpUrl
from typing import Optional
import litellm
from fyodorov_llm_agents.tools.mcp_tool_service import MCPTool as ToolService
from datetime import datetime

MAX_NAME_LENGTH = 80
MAX_DESCRIPTION_LENGTH = 280
VALID_CHARACTERS_REGEX = r'^[a-zA-Z0-9\s.,!?:;\'"-_]+$'

class Agent(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    api_key: str | None = None
    api_url: HttpUrl | None = None
    tools: list[str] = []
    rag: list[dict] = []
    model: str | None = None
    model_id: int | None = None
    name: str = "My Agent"
    description: str = "My Agent Description"
    prompt: str = "My Prompt"
    prompt_size: int = 10000

    class Config:
        arbitrary_types_allowed = True

    def validate(self):
        Agent.validate_name(self.name)
        Agent.validate_description(self.description)
        Agent.validate_prompt(self.prompt, self.prompt_size)

    def resource_dict(self) -> dict:
        return {
            'id': self.id,
            'created_at': self.created_at,
            'name': self.name,
            'description': self.description,
        }

    @staticmethod
    def validate_name(name: str) -> str:
        if not name:
            raise ValueError('Name is required')
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError('Name exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, name):
            raise ValueError('Name contains invalid characters')
        return name

    @staticmethod
    def validate_description(description: str) -> str:
        if not description:
            raise ValueError('Description is required')
        if len(description) > MAX_DESCRIPTION_LENGTH:
            raise ValueError('Description exceeds maximum length')
        if not re.match(VALID_CHARACTERS_REGEX, description):
            raise ValueError('Description contains invalid characters')
        return description

    @staticmethod
    def validate_prompt(prompt: str, prompt_size: int) -> str:
        if not prompt:
            raise ValueError('Prompt is required')
        if len(prompt) > prompt_size:
            raise ValueError('Prompt exceeds maximum length')
        return prompt

    def to_dict(self) -> dict:
        return self.dict(exclude_none=True)
        # return {
        #     'model': self.model,
        #     'name': self.name,
        #     'description': self.description,
        #     'prompt': self.prompt,
        #     'prompt_size': self.prompt_size,
        #     'tools': self.tools,
        #     'rag': self.rag,
        # }


    async def call_with_fn_calling(self, input: str = "", history = [], user_id: str = "") -> dict:
        litellm.set_verbose = True
        model = self.model
        # Set environmental variable
        if self.api_key.startswith('sk-'):
            model = 'openai/'+self.model
            os.environ["OPENAI_API_KEY"] = self.api_key
            self.api_url = "https://api.openai.com/v1"
        elif self.api_key and self.api_key != '':
            model = 'mistral/'+self.model
            os.environ["MISTRAL_API_KEY"] = self.api_key
            self.api_url = "https://api.mistral.ai/v1"
        else:
            print("Provider Ollama")
            model = 'ollama/'+self.model
            if self.api_url is None:
                self.api_url = "https://api.ollama.ai/v1"

        base_url = str(self.api_url.rstrip('/'))
        messages: list[dict] = [
            {"content": self.prompt, "role": "system"},
            *history,
            { "content": input, "role": "user"},
        ]
        # tools
        print(f"Tools: {self.tools}")
        mcp_tools = []
        for tool in self.tools:
            try:
                tool_instance = await ToolService.get_by_name_and_user_id(tool, user_id)
                mcp_tools.append(tool_instance)
            except Exception as e:
                print(f"Error fetching tool {tool}: {e}")
        
        tool_schemas = [tool.get_function() for tool in mcp_tools]
        print(f"Tool schemas: {tool_schemas}")
        if tool_schemas:
            print(f"calling litellm with model {model}, messages: {messages}, max_retries: 0, history: {history}, base_url: {base_url}, tools: {tool_schemas}")
            response = litellm.completion(model=model, messages=messages, max_retries=0, base_url=base_url)
        else:     
            print(f"calling litellm with model {model}, messages: {messages}, max_retries: 0, history: {history}, base_url: {base_url}")
            response = litellm.completion(model=model, messages=messages, max_retries=0, base_url=base_url)
        print(f"Response: {response}")

        message = response.choices[0].message

        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_call = message.tool_calls[0]
            fn_name = tool_call.function.name
            args = tool_call.function.arguments

            mcp_tool = mcp_tools.get(fn_name)
            if not mcp_tool:
                raise ValueError(f"Tool '{fn_name}' not found in loaded MCP tools")

            tool_output = mcp_tool.call(args)

            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_output,
            })

            followup = litellm.completion(
                model=model,
                messages=messages,
                max_retries=0,
                base_url=base_url,
            )
            return {"answer": followup.choices[0].message.content}
        
        answer = message.content
        print(f"Answer: {answer}")
        return {
            "answer": answer,

        }

    @staticmethod
    def call_api(url: str = "", method: str = "GET", body: dict = {}) -> dict:
        if not url:
            raise ValueError('API URL is required')
        try:
            res = requests.request(
                method=method,
                url=url,
                json=body,
            )
            if res.status_code != 200:
                raise ValueError(f"Error fetching API json from {url}: {res.status_code}")
            json = res.json()
            return json
        except Exception as e:
            print(f"Error calling API: {e}")
            raise
    
    @staticmethod
    def from_yaml(yaml_str: str):
        """Instantiate Agent from YAML."""
        if not yaml_str:
            raise ValueError('YAML string is required')
        agent_dict = yaml.safe_load(yaml_str)
        agent = Agent(**agent_dict)
        agent.validate()
        return agent

    @staticmethod
    def from_dict(agent_dict: dict):
        """Instantiate Agent from dict."""
        if not agent_dict:
            raise ValueError('Agent dict is required')
        agent = Agent(**agent_dict)
        agent.validate()
        return agent
