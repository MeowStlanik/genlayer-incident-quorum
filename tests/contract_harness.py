"""Dependency-free LOGIC harness. Not a GenVM emulator or proof of real AI consensus.
Loads the original contract source, with a minimal gl/storage adapter. Every nondet
call runs both leader and independent validator. Unit tests control model/web data.
"""
import copy
import runpy
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UserError(Exception):
    pass


class Return:
    def __init__(self, calldata):
        self.calldata = calldata


class Address(str):
    pass


class Contract:
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        for key, annotation in cls.__annotations__.items():
            origin = getattr(annotation, '__origin__', annotation)
            setattr(obj, key, origin())
        return obj


class Harness:
    def __init__(self, project, contract_class):
        self.outputs = []
        self.calls = 0
        self.pages = {}
        self.web_calls = []
        self.last_validator = None
        self.gl = types.SimpleNamespace(Contract=Contract,
            public=types.SimpleNamespace(write=lambda f:f, view=lambda f:f),
            message=types.SimpleNamespace(sender_address=Address('sponsor')),
            vm=types.SimpleNamespace(UserError=UserError, Return=Return, run_nondet_unsafe=self.run),
            nondet=types.SimpleNamespace(exec_prompt=self.prompt, web=types.SimpleNamespace(get=self.get)))
        module=types.ModuleType('genlayer')
        module.gl=self.gl;module.Address=Address;module.TreeMap=dict;module.DynArray=list;module.u32=int
        previous=sys.modules.get('genlayer');sys.modules['genlayer']=module
        try:self.ns=runpy.run_path(str(ROOT/'contract.py'))
        finally:
            if previous is None:sys.modules.pop('genlayer',None)
            else:sys.modules['genlayer']=previous
        self.contract=self.ns[contract_class]()

    def prompt(self, prompt, response_format):
        assert response_format == 'json'
        self.calls += 1
        if not self.outputs:raise AssertionError('Unexpected inference call')
        return copy.deepcopy(self.outputs.pop(0))

    def get(self, url):
        self.web_calls.append(url)
        body=self.pages[url]
        return types.SimpleNamespace(status_code=200, body=body.encode())

    def run(self, leader, validator):
        result=leader()
        self.last_validator=validator
        if not validator(Return(copy.deepcopy(result))):raise UserError('consensus rejected')
        return result

    def respond(self, leader, validator=None):
        self.outputs.extend([leader, leader if validator is None else validator])
