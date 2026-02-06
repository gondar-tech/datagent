from dataclasses import dataclass, field
from typing import Type
from ..base import BaseAgent
from ..schemas import AgentInput, AgentOutput
from ..registry import AgentRegistry

@dataclass(frozen=True, kw_only=True)
class TrainingPlannerInput(AgentInput):
    goal: str

@dataclass(frozen=True, kw_only=True)
class TrainingPlannerOutput(AgentOutput):
    plan: str

@AgentRegistry.register("training_planner")
class TrainingPlannerAgent(BaseAgent[TrainingPlannerInput, TrainingPlannerOutput]):
    @property
    def input_type(self) -> Type[TrainingPlannerInput]:
        return TrainingPlannerInput

    @property
    def output_type(self) -> Type[TrainingPlannerOutput]:
        return TrainingPlannerOutput

    async def a_run(self, input_data: TrainingPlannerInput) -> TrainingPlannerOutput:
        # Simulate planning logic
        plan = f"""
        Training Plan for: {input_data.goal}
        ------------------------------------
        1. Data Preparation:
           - Source: Detected from goal or defaults
           - Action: Normalize and Split (80/10/10)
        
        2. Model Selection:
           - Architecture: ResNet50 (Assumed for vision) or Transformer (for NLP)
           - Pretrained: True
        
        3. Training Config:
           - Epochs: 10
           - Batch Size: 32
           - Learning Rate: 1e-4
           - Optimizer: AdamW
        
        4. Resource Requirements:
           - 1x GPU Node (Ray Cluster)
        """
        return TrainingPlannerOutput(
            session_id=input_data.session_id,
            plan=plan
        )
