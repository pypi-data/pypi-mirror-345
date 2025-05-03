import importlib
import types
from askmydb.askmydb import AskMyDB
from askmydb import llm as LLM

__all__ = ['AskMyDB', 'LLM']
__version__ = "0.1.5"


def _lazy_llm():
    return importlib.import_module("askmydb.llm")

LLM = types.SimpleNamespace(__getattr__=lambda _, name: getattr(_lazy_llm(), name))
