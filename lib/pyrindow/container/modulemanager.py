from pyrindow.stdlib.datastructure import DictReplaceRecursive
from pyrindow.container.container import GetGlobalContainer
from pyrindow.container.container import Container
from importlib import import_module
import threading

default = None

def DefaultModuleManager(config):
    lock = threading.RLock()
    global default
    with lock:
        if(default):
            return default
        default = ModuleManager(config)
        return default

def getServiceLocator():
    if(default==None):
        raise Exception('ModuleManager is not initialized.')
    return default.getServiceLocator()

def get(name):
    if(default==None):
        raise Exception('ModuleManager is not initialized.')
    return default.getServiceLocator().get(name)

class ModuleManager(object):
    def __init__(self,config):
        self._lock = threading.RLock()
        self._moduleManagerConfig = config
        self._mergedConfig = None
        self._serviceContainer = None
        self._initialized = False

    def getConfig(self):
        with self._lock:
            if self._mergedConfig:
                return self._mergedConfig
            self._mergedConfig = self._getStaticConfig()
            DictReplaceRecursive(self._mergedConfig,self._moduleManagerConfig)
            return self._mergedConfig

    def _getStaticConfig(self):
        config = {}
        if 'module_manager' not in self._moduleManagerConfig:
            raise Exception('Configuration is not specified for ModuleManager.')
        if 'modules' not in self._moduleManagerConfig['module_manager']:
            raise Exception('modules are not defined in module manager configuration.')
        moduleNames = self._moduleManagerConfig['module_manager']['modules']
        for moduleName,enable in moduleNames.items():
            if(enable):
                module = import_module(moduleName)
                DictReplaceRecursive(config,module.getConfig())
        return config

    def getServiceLocator(self):
        self.init()
        return self._getServiceContainer()

    def _getServiceContainer(self):
        if self._serviceContainer:
            return self._serviceContainer
        config = self.getConfig()
        containerConfig = config.get('container',{})
        if config['module_manager'].get('use_global_container'):
            self._serviceContainer = GetGlobalContainer(containerConfig)
        else:
            self._serviceContainer = Container(containerConfig)
        return self._serviceContainer

    def init(self):
        if self._initialized:
            return
        config = self.getConfig()
        container = self._getServiceContainer()
        container.setInstance('config',config)
        container.setInstance('ServiceLocator',container)
        self._initialized = True
