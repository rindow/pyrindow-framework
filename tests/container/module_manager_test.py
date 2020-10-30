"""module manager"""
from pyrindow.container.module_manager import ModuleManager
from pyrindow.container.container import Container, Name, Inject

config = {
    'container': {
        'components':{
            'testComponent':{
                'class':'tests.container.module_manager_test.TestComponent',
            },
        },
    },
    'foo': {
        'boo': {
            'foo':'bar',
        },
    },
}

def get_config():
    return config


@Name('module_manager_test_AnnotatedSubComponent')
class TstAnnotatedSubComponent():
    def __init__(self):
        pass

@Name('module_manager_test_AnnotatedComponent')
class TstAnnotatedComponent():
    @Inject(test=('ref','module_manager_test_alias2'))
    def __init__(self,test=None):
        self.test = test


def test_get_servicelocator():
    config = {
        'module_manager': {
            'modules':{
                'tests.container.module_manager_test':True,
            },
        },
    }
    module_manager = ModuleManager(config)
    config2 = module_manager.get_config()
    assert 'bar'==config2['foo']['boo']['foo']
    container = module_manager.get_service_locator()
    assert isinstance(container,Container)


def test_global_container():
    config = {
        'module_manager': {
            'modules':{
                'tests.container.module_manager_test':True,
            },
            'use_global_container':True,
        },
        'container':{
            'aliases': {
                'module_manager_test_alias':'module_manager_test_AnnotatedComponent',
                'module_manager_test_alias2':'module_manager_test_AnnotatedSubComponent',
            },
        },
    }
    module_manager = ModuleManager(config)
    container = module_manager.get_service_locator()
    assert isinstance(container,Container)
    test = container.get('module_manager_test_alias')
    assert isinstance(test, TstAnnotatedComponent)
    assert isinstance(test.test, TstAnnotatedSubComponent)


def test_safe_config1():
    config = {
        'module_manager': {
            'modules':{
                'tests.container.module_manager_test':True,
            },
        },
        'foo': {
            'boo': {
                'foo1': 'bar1',
            },
        },
    }
    module_manager = ModuleManager(config)
    config2 = module_manager.get_config()
    assert 'bar'==config2['foo']['boo']['foo']
    assert 'bar1'==config2['foo']['boo']['foo1']
    assert config2.get('foo').get('boo').get('foo2') is None

    container = module_manager.get_service_locator()
    assert isinstance(container,Container)

    config3 = container.get('config')
    assert 'bar1'==config3['foo']['boo']['foo1']
    assert config3.get('foo').get('boo').get('foo2') is None


def test_safe_config2():
    config = {
        'module_manager': {
            'modules':{
                'tests.container.module_manager_test':True,
            },
        },
        'foo': {
            'boo': {
                'foo2': 'bar2',
            },
        },
    }
    module_manager = ModuleManager(config)
    config2 = module_manager.get_config()
    assert 'bar'==config2['foo']['boo']['foo']
    assert 'bar2'==config2['foo']['boo']['foo2']
    assert config2.get('foo').get('boo').get('foo1') is None
    container = module_manager.get_service_locator()
    assert isinstance(container,Container)
    config3 = container.get('config')
    assert 'bar2'==config3['foo']['boo']['foo2']
    assert config3.get('foo').get('boo').get('foo1') is None
