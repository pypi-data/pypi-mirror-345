import os
from pathlib import Path

import pytest

from any_agent import AgentConfig, AgentFramework, AnyAgent
from any_agent.config import TracingConfig
from any_agent.tools import search_web, show_final_answer, visit_webpage


@pytest.mark.skipif(
    os.environ.get("ANY_AGENT_INTEGRATION_TESTS", "FALSE").upper() != "TRUE",
    reason="Integration tests require `ANY_AGENT_INTEGRATION_TESTS=TRUE` env var",
)
def test_load_and_run_multi_agent(
    agent_framework: AgentFramework, tmp_path: Path
) -> None:
    kwargs = {}

    if agent_framework is AgentFramework.TINYAGENT:
        pytest.skip(
            f"Skipping test for {agent_framework.name} because it does not support multi-agent"
        )

    kwargs["model_id"] = "gpt-4.1-nano"
    if "OPENAI_API_KEY" not in os.environ:
        pytest.skip(f"OPENAI_API_KEY needed for {agent_framework.name}")

    main_agent = AgentConfig(
        instructions="Use the available agents to complete the task.",
        description="The orchestrator that can use other agents.",
        model_args={"parallel_tool_calls": False}
        if agent_framework is not AgentFramework.AGNO
        else {},
        **kwargs,  # type: ignore[arg-type]
    )

    managed_agents = [
        AgentConfig(
            name="search_web_agent",
            model_id="gpt-4.1-nano",
            description="Agent that can search the web",
            tools=[search_web],
        ),
        AgentConfig(
            name="visit_webpage_agent",
            model_id="gpt-4.1-nano",
            description="Agent that can visit webpages",
            tools=[visit_webpage],
        ),
    ]
    if agent_framework is not AgentFramework.SMOLAGENTS:
        managed_agents.append(
            AgentConfig(
                name="final_answer_agent",
                model_id="gpt-4.1-nano",
                description="Agent that can show the final answer",
                tools=[show_final_answer],
                handoff=True,
            ),
        )
    agent = AnyAgent.create(
        agent_framework=agent_framework,
        agent_config=main_agent,
        managed_agents=managed_agents,
        tracing=TracingConfig(console=False, save=True, cost_info=True),
    )
    result = agent.run("Which agent framework is the best?")

    assert result
    assert result.final_output
    if agent_framework not in [AgentFramework.LLAMA_INDEX]:
        # Llama Index doesn't currently give back raw_responses.
        assert result.raw_responses
        assert len(result.raw_responses) > 0
    if agent_framework not in (
        AgentFramework.AGNO,
        AgentFramework.GOOGLE,
        AgentFramework.TINYAGENT,
    ):
        assert result.trace is not None
        cost_sum = result.trace.get_total_cost()
        assert cost_sum.total_cost > 0
        assert cost_sum.total_cost < 1.00
        assert cost_sum.total_tokens > 0
        assert cost_sum.total_tokens < 20000
