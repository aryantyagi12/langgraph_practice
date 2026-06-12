from typing import TypedDict
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display

class Portfoliostate(TypedDict):
    amount_usd:float
    total_usd:float
    total_inr:float
def cla_total(state:Portfoliostate)->Portfoliostate:
    state["total_usd"]=state["amount_usd"]*1.08
    return state 
def convert_inr(state:Portfoliostate)->Portfoliostate:
    state["total_inr"]=state["total_usd"]*85
    return state
builder=StateGraph(Portfoliostate)
builder.add_node("calculate_total",cla_total)
builder.add_node("conv_inr",convert_inr)
builder.add_edge(START,"calculate_total")
builder.add_edge("calculate_total","conv_inr")
builder.add_edge("conv_inr",END)
graph=builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
print(graph.get_graph().draw_mermaid())
print(graph.invoke({"amount_usd":100}))