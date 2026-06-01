from langchain.tools import tool
import os
    
from langchain.agents import create_agent
from langchain_openrouter import ChatOpenRouter

import app.modules.production.service

import uuid

from pathlib import Path

BASE_DIR = Path(__file__).parent / "simulation_service"

FILES = {
    "simulation_engine": BASE_DIR / "simulation_engine.py",

    "airjet_spinning": BASE_DIR / "spinning" / "airjet.py",
    "rotor_spinning": BASE_DIR / "spinning" / "rotor.py",

    "dobby_weaving": BASE_DIR / "weaving" / "dobby.py",
    "plain_weaving": BASE_DIR / "weaving" / "plain.py",

    "warp_knitting": BASE_DIR / "knitting" / "warp_knitting.py",
    "weft_knitting": BASE_DIR / "knitting" / "weft_knitting.py",

    "reactive_dyeing": BASE_DIR / "coloring" / "reactive_dyeing.py",

    "rotary_printing": BASE_DIR / "printing" / "rotary_printing.py",
    "screen_printing": BASE_DIR / "printing" / "screen_printing.py",
}

@tool("list_files", description="List all available files in the simulation service for understanding the machines.")
def list_files():
    return list(FILES.keys())

@tool("read_file", description="Read the content of a specific file to understand the machine's working principle. Input should be the file name from the list of available files.")
def read_file(file_name: str):
    if file_name not in FILES:
        return f"File '{file_name}' not found. Please choose from the available files: {list(FILES.keys())}"
    
    file_path = FILES[file_name]
    print("Attempting to read file:", file_path)
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file '{file_name}': {str(e)}"

SYSTEM_PROMPT = """
    You are a textile machine expert. The user will ask you questions about how different machines in a textile production line work.
    You have access to a set of tools that allow you to read the content of files describing the working principles of various machines.
    When the user asks about a machine, first use the 'list_files' and then 'read_file' tool to find and read the relevant file(s) that describe how that machine works. Then, based on the content of those files, provide a clear and concise explanation of the machine's working principle to the user.
    Always refer to the files for accurate information and avoid making assumptions without checking the content first.
    
    Rules :
    - Be brief and succinct in your explanations, focusing on the key principles of how the machine operates. No long technical details unless specifically asked for.
    - If the user asks about a machine, identify the relevant file(s) that describe that machine using the 'list_files' tool.
    - Use the 'read_file' tool to read the content of the identified file(s).
    - Don't read every file at once, only read the ones that are relevant to the user's question.
    - Don't get trapped in a cycle of reading files without providing an answer. Always provide an explanation after reading the relevant file(s).
    - Don't write code or formulas in your explanations, just describe the working principle in simple terms.
    - Don't reveal what's in the files directly, but rather synthesize the information to explain how the machine works.
"""

def explain_warning(warning: str) -> str:
    llm = ChatOpenRouter(
        model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=[list_files, read_file],
        system_prompt=SYSTEM_PROMPT
    )
    
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": "My production line has a warning: " + warning + ". Could you please explain what it means and how to fix it?"}
        ]
    })
    
    return result["messages"][-1].content