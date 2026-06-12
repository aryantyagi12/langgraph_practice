from typing import TypedDict,Literal
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display

class Portfoliostate(TypedDict):
    amount_usd:float
    total_usd:float
    target_currency:Literal["eur","inr"]
    total:float
def cla_total(state:Portfoliostate)->Portfoliostate:
    state["total_usd"]=state["amount_usd"]*1.08
    return state
def conv_inr(state:Portfoliostate)->Portfoliostate:
    state["total"]=state["total_usd"]*85
    return state
def conv_eur(state:Portfoliostate)->Portfoliostate:
    state["total"]=state["total_usd"]*0.93
    return state
def decide(state:Portfoliostate)->Portfoliostate:
    return state["target_currency"]
builder=StateGraph(Portfoliostate)
builder.add_node("calculate_total",cla_total)
builder.add_node("convert_inr",conv_inr)
builder.add_node("convert_eur",conv_eur)
builder.add_edge(START,"calculate_total")
builder.add_conditional_edges(
    "calculate_total",
    decide,
    {
        "inr": "convert_inr",
        "eur": "convert_eur"
    }
)
builder.add_edge("convert_inr",END)
builder.add_edge("convert_eur",END)
graph=builder.compile()
display(Image(graph.get_graph().draw_mermaid_png()))
print(graph.get_graph().draw_mermaid())
print(graph.invoke({"amount_usd":100,"target_currency":"eur"}))