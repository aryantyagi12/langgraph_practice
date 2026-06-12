from typing import Annotated
from dotenv import load_dotenv
import os
load_dotenv()
from typing import TypedDict,Literal
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display
from  langgraph.graph.message import add_messages
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)   

class State(TypedDict):
    message:Annotated[list,add_messages]
def chatbot(state:State)->State:
    return {"message":[llm.invoke(state["message"])]}
builder=StateGraph(State)
builder.add_node("chatbot",chatbot)
builder.add_edge(START,"chatbot")
builder.add_edge("chatbot",END)
graph=builder.compile()
message={"role":"user","content":"what is the capital of india? print only name"}
result=graph.invoke({"message":[message]})
print(result["message"][-1].content)



