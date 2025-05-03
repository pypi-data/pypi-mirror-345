from typing import Callable

from pydantic import BaseModel
from octostar_streamlit.core.method_call import MethodCall
from streamlit.runtime.scriptrunner import get_script_run_ctx
import streamlit as st

def has_state_changed(idn: str):
    """
    Suppossed to guard against re-execution on re-renders due to re-size, etc.
    But this guard doesn't work
    """
    script_ctx = get_script_run_ctx()
    print(f"script_ctx: {id(script_ctx.script_requests)}")
    if "__streamlit-octostar" not in st.session_state:
        st.session_state["__streamlit-octostar"] = {}

    if f"{idn}-prev_req" not in st.session_state["__streamlit-octostar"]:
        script_ctx = get_script_run_ctx()
        st.session_state["__streamlit-octostar"][f"{idn}-prev_req"] = script_ctx.script_requests
    elif id(script_ctx.script_requests) == id(st.session_state["__streamlit-octostar"][f"{idn}-prev_req"]):
        print("False")
        return False

    st.session_state["__streamlit-octostar"][f"{idn}-prev_req"] = script_ctx.script_requests
    return True

class StreamlitMethodExecutor:
    def __init__(self, method_call: MethodCall, fn: Callable, key=None, subscribe=None) -> None:
        self._method_call = method_call
        self._fn = fn
        self._key = key
        self._subscribe = subscribe

    def execute(self):
        key = self._key
        service = self._method_call.service
        method = self._method_call.method

        if not has_state_changed(idn=f"{key}-{service}-{method}"):
            return

        if isinstance(self._method_call.params, BaseModel):
            params = self._method_call.params.model_dump(by_alias=True)
        else:
            params = self._method_call.params

        return self._fn(service=service, method=method, params=params, key=key, subscribe=self._subscribe)
