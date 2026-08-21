"""Compile the investment graph with a durable SQLite checkpointer."""

import sqlite3

import streamlit as st
from langgraph.checkpoint.sqlite import SqliteSaver

from config import config
from graph import build_investment_graph


@st.cache_resource
def build_investment_workflow():
    connection = sqlite3.connect(
        config.checkpoint_db_path,
        check_same_thread=False,
    )
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return build_investment_graph().compile(checkpointer=checkpointer)
