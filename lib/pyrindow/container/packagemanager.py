from rindow.stdlib.datastructure import DictReplaceRecursive
from rindow.container.container import GetGlobalContainer
from rindow.container.container import Container
from importlib import import_module
import threading

class PackageManager(object):
    def __init__(self,config):
        self._lock = threading.RLock()
        self._packageManagerConfig = config
        self._mergedConfig = None
        self._serviceContainer = None
        self._initialized = False

    def getConfig(self):
        with self._lock:
            if self._mergedConfig:
                return self._mergedConfig
            self._mergedConfig = self._getStaticConfig()
            DictReplaceRecursive(self._mergedConfig,self._packageManagerConfig)
            return self._mergedConfig

    def _getStaticConfig(self):
        config = {}
        if 'package_manager' not in self._packageManagerConfig:
            raise Exception('Configuration is not specified for packageManager.')
        if 'packages' not in self._packageManagerConfig['package_manager']:
            raise Exception('packages are not defined in package manager configuration.')
        packageNames = self._packageManagerConfig['package_manager']['packages']
        for packageName in packageNames:
            package = import_module(packageName)
            DictReplaceRecursive(config,package.getConfig())
        return config

    def getServiceLocator(self):
        self.init()
        return self._getServiceContainer()

    def _getServiceContainer(self):
        if self._serviceContainer:
            return self._serviceContainer
        config = self.getConfig()
        containerConfig = config.get('container',{})
        if config['package_manager'].get('use_global_container'):
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
        self._initialized = True
