import json
import time
from anthropic import Anthropic
from tracer import log_tool_call
from constants import MODEL, WORKER_MAX_TOKENS

client = Anthropic()


class Worker:
    def __init__(
        self,
        name: str,
        specialty: str,
        tools: list[dict],
        tool_executor,
    ):
        self.name = name
        self.specialty = specialty
        self.tools = tools
        self._executor = tool_executor

    def run(self, task: str) -> str:
        system = (
            f"You are a {self.specialty} specialist investigating a production incident. "
            "Use your tools to gather data, then return a concise findings summary."
        )
        messages = [{"role": "user", "content": task}]

        for _ in range(8):
            response = client.messages.create(
                model=MODEL,
                max_tokens=WORKER_MAX_TOKENS,
                system=system,
                tools=self.tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return ""

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        start = time.time()
                        result = self._executor(block.name, block.input)
                        latency_ms = int((time.time() - start) * 1000)
                        log_tool_call(self.name, block.name, block.input, result, latency_ms)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return ""
