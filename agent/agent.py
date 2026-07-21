import os
import json
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from skills import web_search
from plugins import read_file
from memory import Memory
from hooks import before_tool_call, after_tool_call

load_dotenv()
client = Anthropic()
MODEL = "claude-haiku-4-5"

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current information. Returns top 3 results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": "Read contents of a .txt or .pdf file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to read"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "remember",
        "description": "Store a fact in memory to recall later.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fact": {"type": "string", "description": "The fact to remember"}
            },
            "required": ["fact"],
        },
    },
]


def run_tool(name: str, tool_input: dict, memory: Memory) -> str:
    start = time.time()
    before_tool_call(name, tool_input)
    if name == "web_search":
        result = web_search(tool_input["query"])
    elif name == "read_file":
        result = read_file(tool_input["path"])
    elif name == "remember":
        memory.add(tool_input["fact"])
        result = f"Remembered: {tool_input['fact']}"
    else:
        result = f"Unknown tool: {name}"
    duration_ms = int((time.time() - start) * 1000)
    after_tool_call(name, result, duration_ms)
    return result


def run_agent(question: str, memory: Memory) -> str:
    memories = memory.get_all()
    system_prompt = "You are a helpful AI assistant with access to tools."
    if memories:
        system_prompt += f"\n\nThings you remember from earlier:\n{memories}"

    messages = [{"role": "user", "content": question}]
    print(f"\n{'='*60}\nQuestion: {question}\n{'='*60}")

    for _ in range(10):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nAnswer: {block.text}")
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n→ Calling tool: {block.name}({json.dumps(block.input)})")
                    result = run_tool(block.name, block.input, memory)
                    print(f"← Result preview: {result[:200]}{'...' if len(result) > 200 else ''}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return ""
