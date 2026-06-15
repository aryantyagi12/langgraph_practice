from langgraph.types import interrupt, Command
from typing import TypedDict,Annotated
import time
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display
from langgraph.graph.message import add_messages

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode,tools_condition
from langsmith import traceable

from dotenv import load_dotenv
load_dotenv()


class State(TypedDict):
    messages:Annotated[list,add_messages]


@tool
def get_stock_price(symbol:str)->float:
    """Returns the current stock price for a given ticker symbol."""
    return {
        "MSFT":250,
        "AAPL":150,
        "GOOG":100
    }.get(symbol,0.0)
@tool
def buy_stocks(symbol:str,amount:int,price:float)->str:
    """Buys stocks of a given symbol."""
    decision=interrupt(f"appprove buying {amount}{symbol} stocks for the price of {price}")
    if decision == "yes":
        return f"You bought {amount} stocks of {symbol} at {price} each for a total of {amount*price}"
    else:
        return "You rejected the stocks"
tools=[get_stock_price,buy_stocks]
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
llm_with_tools=llm.bind_tools(tools)

def chatbot(state:State)->State:
    return {"messages":[llm_with_tools.invoke(state["messages"])]}

builder=StateGraph(State)
builder.add_node("chatbot",chatbot)
builder.add_node("tools",ToolNode(tools))
builder.add_edge(START,"chatbot")
builder.add_conditional_edges("chatbot",tools_condition)
builder.add_edge("tools","chatbot")

memory=MemorySaver()
graph=builder.compile(checkpointer=memory)

print(display(Image(graph.get_graph().draw_mermaid_png())))
print(graph.get_graph().draw_mermaid())

# --- Invoke 1: Ask about stock prices ---
config={"configurable":{"thread_id":"1"}}
state=graph.invoke({"messages":[{"role":"user","content":"what is the current price of MSFT?"}]},config=config)
print("Turn 1:", state["messages"][-1].content)

state=graph.invoke({"messages":[{"role":"user","content":"buy 10 MSFT at current price"}]},config=config)
print(state["messages"][-1].content)

decision=input("approved yes/no")
state=graph.invoke(Command(resume=decision),config=config)
print(state["messages"][-1].content)

