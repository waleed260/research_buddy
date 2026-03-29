"""Guardrails for input/output validation."""

import re
from typing import Any
from agents import InputGuardrail, OutputGuardrail, GuardrailFunctionOutput, TResponseInputItem
from pydantic import BaseModel


class InputValidationResult(BaseModel):
    """Result of input validation."""
    is_valid: bool
    reason: str = ""
    sanitized_input: str = ""


class OutputValidationResult(BaseModel):
    """Result of output validation."""
    is_valid: bool
    reason: str = ""
    quality_score: float = 0.0


def check_harmful_content(text: str) -> bool:
    """Check for potentially harmful content patterns."""
    harmful_patterns = [
        r"\b(hack|crack|exploit)\s+(system|account|password)",
        r"\b(create|make)\s+(bomb|weapon|malware|virus)",
        r"\b(how to)\s+(steal|hack|attack|destroy)",
        r"\b(bypass|circumvent)\s+(security|authentication)",
    ]
    text_lower = text.lower()
    for pattern in harmful_patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def check_research_topic_safety(topic: str) -> InputValidationResult:
    """Validate that a research topic is safe and appropriate."""
    if not topic or len(topic.strip()) == 0:
        return InputValidationResult(
            is_valid=False,
            reason="Empty topic provided"
        )
    
    if len(topic) > 2000:
        return InputValidationResult(
            is_valid=False,
            reason="Topic too long (max 2000 characters)"
        )
    
    if check_harmful_content(topic):
        return InputValidationResult(
            is_valid=False,
            reason="Topic contains potentially harmful content"
        )
    
    # Sanitize input
    sanitized = topic.strip()
    return InputValidationResult(
        is_valid=True,
        sanitized_input=sanitized
    )


async def input_guardrail_function(
    input_data: list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """Guardrail function for validating user input."""
    # Extract the latest user message
    if not input_data:
        return GuardrailFunctionOutput(
            input_guardrail_output=[InputValidationResult(
                is_valid=False,
                reason="No input provided"
            ).model_dump()],
            tripwire_triggered=False
        )
    
    last_message = input_data[-1]
    if isinstance(last_message, dict):
        content = last_message.get("content", "")
    else:
        content = str(last_message)
    
    validation = check_research_topic_safety(content)
    
    return GuardrailFunctionOutput(
        input_guardrail_output=[validation.model_dump()],
        tripwire_triggered=not validation.is_valid
    )


async def output_guardrail_function(
    output_data: Any
) -> GuardrailFunctionOutput:
    """Guardrail function for validating agent output."""
    if output_data is None:
        return GuardrailFunctionOutput(
            input_guardrail_output=[OutputValidationResult(
                is_valid=False,
                reason="Empty output"
            ).model_dump()],
            tripwire_triggered=True
        )
    
    # Extract text from output
    if isinstance(output_data, str):
        text = output_data
    elif isinstance(output_data, dict):
        text = str(output_data.get("output", output_data.get("findings", "")))
    else:
        text = str(output_data)
    
    # Check for harmful content in output
    if check_harmful_content(text):
        return GuardrailFunctionOutput(
            input_guardrail_output=[OutputValidationResult(
                is_valid=False,
                reason="Output contains potentially harmful content"
            ).model_dump()],
            tripwire_triggered=True
        )
    
    # Check output quality (basic checks)
    quality_score = 0.5  # Base score
    
    if len(text) > 100:
        quality_score += 0.2
    
    # Check for structured content
    if any(marker in text for marker in ["##", "**", "- ", "1.", "Sources:"]):
        quality_score += 0.3
    
    validation = OutputValidationResult(
        is_valid=True,
        quality_score=min(quality_score, 1.0)
    )
    
    return GuardrailFunctionOutput(
        input_guardrail_output=[validation.model_dump()],
        tripwire_triggered=False
    )


# Create guardrail instances
input_guardrail = InputGuardrail(
    name="research_input_validator",
    guardrail_function=input_guardrail_function,
)

output_guardrail = OutputGuardrail(
    name="research_output_validator",
    guardrail_function=output_guardrail_function,
)
