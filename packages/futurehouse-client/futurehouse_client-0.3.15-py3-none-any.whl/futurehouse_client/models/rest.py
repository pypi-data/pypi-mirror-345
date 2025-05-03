from pydantic import BaseModel, JsonValue


class FinalEnvironmentRequest(BaseModel):
    status: str


class StoreAgentStatePostRequest(BaseModel):
    agent_id: str
    step: str
    state: JsonValue
    trajectory_timestep: int


class StoreEnvironmentFrameRequest(BaseModel):
    agent_state_point_in_time: str
    current_agent_step: str
    state: JsonValue
    trajectory_timestep: int
