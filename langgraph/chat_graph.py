
import os
from dotenv import load_dotenv


from typing_extensions import TypedDict
from typing import Annotated

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver

from psycopg.rows import dict_row
import psycopg

from langchain_groq import ChatGroq

load_dotenv()

# ==================================================
# ENV VARIABLES
# ==================================================

DB_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ==================================================
# LLM
# ==================================================

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    streaming=True
)

# ==================================================
# STATE
# ==================================================

class ChatState(TypedDict):

    messages: Annotated[list, add_messages]

# ==================================================
# POSTGRES CHECKPOINTER
# ==================================================

#
def create_checkpointer():

    conn = psycopg.connect(
        DB_URL,
        autocommit=True,
        row_factory=dict_row
    )

    checkpointer = PostgresSaver(conn)

    # Create tables automatically
    checkpointer.setup()

    return checkpointer

checkpointer = create_checkpointer()

# ==================================================
# CHAT NODE
# ==================================================

def chat_node(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }

# ==================================================
# GRAPH
# ==================================================

builder = StateGraph(ChatState)

builder.add_node("chat", chat_node)

builder.set_entry_point("chat")

builder.set_finish_point("chat")

graph = builder.compile(
    checkpointer=checkpointer
)

