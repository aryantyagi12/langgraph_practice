from typing import TypedDict,Annotated
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display
from langgraph.graph.message import add_messages

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver


from langgraph.prebuilt import ToolNode,tools_condition

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
tools=[get_stock_price]
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
builder.add_edge("tools","chatbot")  # after tool runs, go back to chatbot
#memory added
memory=MemorySaver()

graph=builder.compile(checkpointer=memory)
print(display(Image(graph.get_graph().draw_mermaid_png())))
print(graph.get_graph().draw_mermaid())

#first thread
config={"configurable":{"thread_id":"1"}}
state=graph.invoke({"messages":[{"role": "user", "content": "i want to buy 20 GOOG stocks using current price.Then 10 apple. what will be the total cost?"}]},config=config)
print(state["messages"][-1].content)

#same thread - continues the conversation with memory
config={"configurable":{"thread_id":"1"}}
state=graph.invoke({"messages":[{"role": "user", "content": "what is the total cost now"}]},config=config)
print(state["messages"][-1].content)



    