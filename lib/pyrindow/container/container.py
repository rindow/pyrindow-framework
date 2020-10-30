from importlib import import_module
import types
import sys
import inspect
import threading

class Container(object):
    def __init__(self,config={},componentManager=None,instanceManager=None):
        self._lock = threading.RLock()
        if(componentManager==None):
            componentManager = ComponentDefinitionManager(config)
        self.componentManager = componentManager
        if(instanceManager==None):
            instanceManager = InstanceManager(config)
        self.instanceManager = instanceManager
    def setInstance(self,name,instance):
        self.instanceManager.set(name,instance);
    def get(self,name):
        with self._lock:
            name = self.componentManager.resolveAlias(name)
            if self.instanceManager.has(name):
                return self.instanceManager.get(name)
            if not self.componentManager.has(name):
                raise Exception('component not found.: '+name)
            component = self.componentManager.get(name)
            if component.getFactoryName():
                instance = self.newInstanceByFactory(component)
            else:
                instance = self.newInstance(component)
            for injectName,injectorArgs in component.getInjectors().items():
                args = self.buildArgs(injectorArgs)
                getattr(instance,injectName)(**args)
            for injectName,propertyValue in component.getProperties().items():
                value = self.resolvValue(propertyValue,injectName)
                setattr(instance,injectName,value)
            self.setInstance(name,instance)
            return instance
    def newInstance(self,component):
        mode = component.getFactoryMode()
        if mode==None or mode=='class':
            classObject = self.getClassObject(component.getClassName())
            if component.hasConstructArgs():
                args = self.buildArgs(component.getConstructArgs())
                instance = classObject(**args)
            else:
                instance = classObject()
        elif mode=='import':
            instance = self.getClassObject(component.getClassName(),moduleMode=True)
        elif mode=='from':
            instance = self.getClassObject(component.getClassName())
        return instance
    def newInstanceByFactory(self,component):
        mode = component.getFactoryMode()
        if mode==None or mode=='function':
            factory = self.getClassObject(component.getFactoryName())
            args = component.getFactoryArgs()
            return factory(self,**args)
        elif mode=='import':
            return self.getClassObject(component.getFactoryName(),moduleMode=True)
        elif mode=='from':
            return self.getClassObject(component.getFactoryName())
        else:
            raise Exception('invalid factory_mode: '+mode)
    def has(self,name):
        return self.componentManager.has(name) or self.componentManager.has(name)
    def buildArgs(self,injectorArgs):
        args = {}
        for name,propertyValue in injectorArgs.items():
            args[name] = self.resolvValue(propertyValue,name)
        return args
    def resolvValue(self,propertyValue,name):
        if not isinstance(propertyValue,dict):
            raise Exception('inject value "%s" must be specified injection type by the dict.' % name)
        if 'value' in propertyValue:
            return propertyValue['value']
        elif 'ref' in propertyValue:
            return self.get(propertyValue['ref'])
        elif 'config' in propertyValue:
            return self.getConfigValue(propertyValue['config'])
        else:
            raise Exception('unknown argument type.')
    def getConfigValue(self,name):
        config = self.get('config')
        for idx in name.split(':'):
            if idx in config:
                config = config[idx]
            else:
                return None
        return config
    def getClassObject(self,fullClassName,moduleMode=False):
        if moduleMode:
            module = import_module(fullClassName)
            return module
        idx = fullClassName.rfind('.')
        if(idx>0):
            moduleName = fullClassName[0:idx]
            className = fullClassName[idx+1:]
        else:
            moduleName = fullClassName
            className = fullClassName
        module = import_module(moduleName)
        return getattr(module,className)

class InstanceManager(object):
    def __init__(self,config={},instances={}):
        self.config = config
        self.instances = instances
    def has(self,name):
        return name in self.instances
    def get(self,name):
        return self.instances.get(name)
    def set(self,name,instance):
        self.instances[name] = instance

class ComponentDefinitionManager(object):
    def __init__(self,config={}):
        self.config = config
        if 'components' not in self.config:
            self.config['components'] = {}
        if 'aliases' not in self.config:
            self.config['aliases'] = {}
    def get(self,name,force=False):
        if force and name not in self.config['components']:
            self.config['components'][name] = {}
            component = ComponentDefinition(name,self.config['components'][name])
            component.setClassName(name)
            return component
        if name not in self.config['components']:
            raise Exception('component "%s" not found' % name)
        return ComponentDefinition(
            name,
            self.config['components'][name])
    def has(self,name):
        name = self.resolveAlias(name)
        return name in self.config['components']
    def set(self,name,component):
        name = self.resolveAlias(name)
        self.config['components'][name] = component.config
    def resolveAlias(self,name):
        if(name in self.config['aliases']):
            name = self.config['aliases'][name]
        return name

class ComponentDefinition(object):
    def __init__(self,name,config={}):
        self.name = name
        if(config==None):
            config = {}
        self.config = config
    def getName(self):
        return self.name
    def getClassName(self):
        return self.config.get('class',self.name)
    def getFactoryName(self):
        return self.config.get('factory')
    def getFactoryMode(self):
        return self.config.get('factory_mode')
    def setClassName(self,className):
        self.config['class'] = className
    def getProperties(self):
        return self.config.get('properties',{})
    def getConstructArgs(self):
        return self.config.get('construct_args',{})
    def getFactoryArgs(self):
        return self.config.get('factory_args',{})
    def getInjectors(self):
        return self.config.get('injectors',{})
    def hasConstructArgs(self):
        return len(self.config.get('construct_args',{})) > 0
    def getInjectorNames(self):
        return self.config.get('injectors',{}).keys()
    def addProperty(self,name,valueType,value):
        self.config.setdefault('properties',{})[name] = { valueType: value }
    def addConstructorArg(self,argName,valueDefinition):
        self.config.setdefault('construct_args',{})[argName] = valueDefinition
    def addInjectorArg(self,name,argName,valueDefinition):
        self.config.setdefault('injectors',{}).setdefault(name,{})[argName] = valueDefinition
    def getValueTypeFromConfig(self,config):
        if('ref' in config):
            return 'ref'
        elif('value' in config):
            return 'value'
        else:
            raise Exception('unkown value type')
    def getValueFromConfig(self,config):
        if('ref' in config):
            return config['ref']
        elif('value' in config):
            return config['value']
        else:
            raise Exception('unkown value type')
    def addPropertyWithReference(self,name,value):
        self.addProperty(self,name,'ref',value)
    def addPropertyWithValue(self,name,value):
        self.addProperty(self,name,'value',value)
    def addInjectorArgWithReference(self,name,argName,value):
        self.addInjectorArg(self,name,argName,{'ref':value})
    def addInjectorArgWithValue(self,name,argName,value):
        self.addInjectorArg(self,name,argName,{'value':value})
    def addConstructorArgWithReference(self,argName,value):
        self.addConstructorArg(self,argName,{'ref':value})
    def addConstructorArgWithValue(self,argName,value):
        self.addConstructorArg(self,argName,{'value':value})

_GlobalLock = threading.RLock()
def GetGlobalContainer(config={}):
    global _globalContainer
    with _GlobalLock:
        try:
            return _globalContainer
        except NameError:
            _globalContainer = Container(config)
            return _globalContainer

def SetGlobalContainer(container):
    global _globalContainer
    _globalContainer = container

def GetGlobalComponentManager(config={}):
    global _globalComponentManager
    with _GlobalLock:
        try:
            return _globalComponentManager
        except NameError:
            _globalComponentManager = ComponentDefinitionManager(config)
            return _globalComponentManager

def Name(name):
    def NameDecorator(classObject):
        if type(classObject)==types.TypeType:
            componentManager = GetGlobalComponentManager()
            componentName = classObject.__module__ + '.' + classObject.__name__
            component = componentManager.get(componentName,True)
            if name:
                componentManager.set(name,component)
        else:
            raise '@Name must decorate to a class.'
        return classObject
    if type(name)==types.TypeType:
        classObject = name
        name = None
        NameDecorator(classObject)
    else:
        return NameDecorator

def Inject(**params):
    def InjectDecorator(method):
        frame = getUpperFrame()
        if type(method)==types.FunctionType:
            componentManager = GetGlobalComponentManager()
            componentName = method.__module__ + '.' + frame.f_code.co_name
            component = componentManager.get(componentName,True)
            for argName,argValue in params.items():
                if method.__name__ == '__init__':
                    component.addConstructorArg(argName,argValue)
                else:
                    component.addInjectorArg(method.__name__,argName,argValue)
        elif isinstance(method,property):
            raise '@Inject is not supported on a property.'
            #print 'this is property'
            #print 'module:', frame.f_globals.get('__name__')
            #print 'class:',frame.f_code.co_name
            #print 'property:',method
            #print dir(method)
        else:
            raise '@Inject must decorate to a method.'
        return method

    def getUpperFrame(frame=None, level=2):
        frame = frame or sys._getframe(level)
        while frame.f_globals.get('__name__') == __name__:
            frame = frame.f_back
        return frame

    return InjectDecorator
