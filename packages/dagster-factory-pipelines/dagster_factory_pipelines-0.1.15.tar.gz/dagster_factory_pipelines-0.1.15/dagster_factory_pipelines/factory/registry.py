from dagster_factory_pipelines.factory.base import AssetCheckBase, ModuleBase, TriggerBase
## Full registry boilerplate provided by GPT and modified for the required used case
MODULE_REGISTRY = {}
HOOK_REGISTRY = {}
RESOURCE_REGISTRY = {}
TRIGGER_REGISTRY = {} # sensors
CHECK_REGISTRY = {} # ASSET CHECK

CHECK_REPO = []
SCHEDULES_REPO = []
RESOURCE_REPO = {}
TRIGGER_REPO = []
ASSET_REPO = []
JOB_REPO = []

def register_check(check_name):
    def wrapper(cls):
        CHECK_REGISTRY[check_name] = cls
        return cls
    return wrapper

def register_hook(hook_name):
    def wrapper(cls):
        HOOK_REGISTRY[hook_name] = cls
        return cls
    return wrapper

def register_module(module_name):
    def wrapper(cls):
        MODULE_REGISTRY[module_name] = cls
        return cls
    return wrapper

def register_resource(resource_name):
    def wrapper(cls):
        RESOURCE_REGISTRY[resource_name] = cls
        return cls
    return wrapper


def register_trigger(trigger_name):
    def wrapper(cls):
        TRIGGER_REGISTRY[trigger_name] = cls
        return cls
    return wrapper

def get_module(module_name: str, params: dict = dict()) -> ModuleBase:
    module_class = MODULE_REGISTRY.get(module_name)
    if module_class:
        return module_class(**params) 
    else:
        raise ValueError(f"Module {module_name} not found")
    
def get_resource(resource_name: str, params: dict = dict()):
    module_class = RESOURCE_REGISTRY.get(resource_name)
    if module_class:
        return module_class(**params)  
    else:
        raise ValueError(f"Resource {resource_name} not found")
    
    
def get_trigger(trigger_name: str, params: dict = dict()) -> TriggerBase:
    module_class = TRIGGER_REGISTRY.get(trigger_name)
    if module_class:
        return module_class(**params)  
    else:
        raise ValueError(f"Trigger {trigger_name} not found")
    

def get_hook(hook_name: str):
    module_class = HOOK_REGISTRY.get(hook_name)
    if module_class:
        return module_class  
    else:
        raise ValueError(f"Hook {hook_name} not found")
    

def get_check(check_name: str, params:dict = dict()) -> AssetCheckBase:
    module_class = CHECK_REGISTRY.get(check_name)
    if module_class:
        return module_class(**params) 
    else:
        raise ValueError(f"Check {check_name} not found")