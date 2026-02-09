import streamlit as st
import os

# Run dashboard.py
with open("dashboard.py", encoding="utf8") as f:
    code = f.read()
    exec(code)
