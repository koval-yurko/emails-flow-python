import os
from .decorators import *

def init_trace():
    if os.getenv("ENVIRONMENT") == 'local':
        from .setup_opentelemetry import setup_opentelemetry
        setup_opentelemetry()