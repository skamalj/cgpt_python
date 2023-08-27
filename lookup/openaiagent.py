from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor

from main import get_insurers, get_data
llm = ChatOpenAI(temperature=0)
tools = [get_data, get_insurers]

system_message = SystemMessage(content="""
You are very powerful assistant, who can easily lookup data using tools provided.
Insurer name must be from the list provided by get_insurer tool. Call that first to identify correct insurer name.
Do not assume any value or input. If a value for tool or function cannot be inferred from input then respond with followup question to get details

""")
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)

agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.run("compare market share of individual premium for reliance and aditya birla?")