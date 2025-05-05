from pydantic import BaseModel, Field


class AgentCapabilities(BaseModel):
    streaming: bool


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    examples: list[str]
    inputModes: list[str] = Field(default_factory=list)
    outputModes: list[str] = Field(default_factory=list)


class MCPServerConfig(BaseModel):
    name: str
    url: str
    transport: str


class AgentConfig(BaseModel):
    name: str
    description: str
    version: str
    capabilities: AgentCapabilities
    skills: list[AgentSkill]
    prompt: str
    mcpServers: list[MCPServerConfig] = Field(default_factory=list)
    supported_content_types: list[str] = Field(default_factory=list)
