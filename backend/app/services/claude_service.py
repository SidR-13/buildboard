from anthropic import Anthropic

from app.config import settings

_ANALYSIS_TOOL = {
    "name": "report_failure_analysis",
    "description": "Report the root cause of a CI build failure and a suggested fix.",
    "input_schema": {
        "type": "object",
        "properties": {
            "root_cause": {
                "type": "string",
                "description": "A concise explanation of why the build failed, based on the logs.",
            },
            "suggested_fix": {
                "type": "string",
                "description": "A concrete, actionable fix for the identified root cause.",
            },
        },
        "required": ["root_cause", "suggested_fix"],
    },
}


def _mock_analysis(logs_snippet: str) -> dict:
    return {
        "root_cause": "[MOCK] Build failed - AI_MOCK=true, no real analysis performed.",
        "suggested_fix": "[MOCK] Set AI_MOCK=false and provide a real ANTHROPIC_API_KEY to get a real fix.",
    }


def analyze_failure(workflow_name: str, branch: str, commit_sha: str, logs_snippet: str) -> dict:
    # Checked before the client is even constructed, so a placeholder dev key can't reach the network.
    if settings.ai_mock:
        return _mock_analysis(logs_snippet)

    client = Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        tools=[_ANALYSIS_TOOL],
        # Forcing the tool call makes the API guarantee the response shape, instead of
        # asking for JSON in the prompt and hoping the text parses.
        tool_choice={"type": "tool", "name": "report_failure_analysis"},
        messages=[
            {
                "role": "user",
                "content": (
                    f"A GitHub Actions workflow run failed.\n"
                    f"Workflow: {workflow_name}\n"
                    f"Branch: {branch}\n"
                    f"Commit: {commit_sha}\n\n"
                    f"Last {len(logs_snippet.splitlines())} lines of logs:\n{logs_snippet}\n\n"
                    f"Identify the root cause and suggest a concrete fix."
                ),
            }
        ],
    )

    tool_use_block = next(block for block in message.content if block.type == "tool_use")
    return tool_use_block.input
