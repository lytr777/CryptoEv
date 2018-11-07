from output.module.logger import LoggerStub
from output.module.debugger import DebuggerStub


class RuntimeConstants:
    def __init__(self):
        self.debugger = DebuggerStub()
        self.logger = LoggerStub()
        self.value_hash = {}
        self.configuration = {}
        self.case_generator = None
        self.cnf = None


runtime_constants = RuntimeConstants()
