from pyrindow.container.container import Container, \
    GetGlobalContainer, Name, Inject

class TstComponent(object):
    def __init__(self,test=None):
        self.test = test

def TstComponentFactory(serviceLocator,test):
    c = TstComponent()
    c.test = test
    return c

TestProperty = TstComponent()
TestProperty.test = 'value4'

testValiable = 'value5'

class TstSubComponent():
    def __init__(self,test=None):
        self.test = test

@Name('container_test_AnnotatedSubComponent')
class TstAnnotatedSubComponent():
    def __init__(self):
        pass

@Name('container_test_AnnotatedComponent')
class TstAnnotatedComponent():
    @Inject(test=('ref','container_test_alias2'))
    def __init__(self,test=None):
        self.test = test


def test_set_and_get():
    cont = Container()
    cont.set_instance('test','value')
    assert 'value'==cont.get('test')

def test_get_with_construct_args():
    config = {
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'construct_args':{
                    'test': ('value','value1'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'value1'==test.test

def test_get_with_property():
    config = {
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'properties':{
                    'test': ('value','value2'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'value2'==test.test

def test_get_with_construct_args_and_property():
    config = {
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'construct_args':{
                    'test': ('value','value1'),
                },
                'properties':{
                    'test2': ('value','value2'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'value1'==test.test
    assert 'value2'==test.test2

def test_get_with_factory_function():
    config = {
        'components': {
            'tstComponent': {
                'factory':'tests.container.container_test.TstComponentFactory',
                'factory_args':{
                    'test': 'value3',
                },
                'properties':{
                    'test2': ('value','value30'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'value3'==test.test
    assert 'value30'==test.test2

def test_get_with_module_property():
    config = {
        'components': {
            'tstComponent': {
                'factory_mode':'property',
                'class':'tests.container.container_test.TestProperty',
                'properties':{
                    'test2': ('value','value40'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'value4'==test.test
    assert 'value40'==test.test2

def test_get_with_import_module():
    config = {
        'components': {
            'tstComponent': {
                'factory_mode':'import',
                'class':'tests.container.container_test',
                'properties':{
                    'test2': ('value','value50'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    # assert isinstance(test,ThisModule)
    assert 'value5'==test.testValiable
    assert 'value50'==test.test2

def test_dependence_injection_with_reference_name():
    config = {
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'properties':{
                    'test2': ('ref','tstSubComponent'),
                },
            },
            'tstSubComponent': {
                'class':'tests.container.container_test.TstSubComponent',
                'properties':{
                    'test': ('value','subValue'),
                },
            },
        },
    }
    cont = Container(config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert isinstance(test.test2,TstSubComponent)
    assert 'subValue'==test.test2.test

def test_injection_config_value():
    config = {
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'properties':{
                    'test2': ('config','testtest:test2:test3'),
                },
            },
        },
        'testtest':{
            'test2': {
                'test3': 'testValue'
            }
        }
    }
    cont = Container(config)
    cont.set_instance('config',config)
    test = cont.get('tstComponent')
    assert isinstance(test,TstComponent)
    assert 'testValue'==test.test2

def test_alias():
    config = {
        'aliases': {
            'test_alias':'tstComponent',
            'test_alias2':'test_alias',
        },
        'components': {
            'tstComponent': {
                'class':'tests.container.container_test.TstComponent',
                'properties':{
                    'test2': ('config','testtest:test2:test3'),
                },
            },
        },
        'testtest':{
            'test2': {
                'test3': 'testValue'
            }
        }
    }
    cont = Container(config)
    cont.set_instance('config',config)
    test = cont.get('test_alias2')
    assert isinstance(test,TstComponent)


def test_annotaion():
    config = {
        'aliases': {
            'container_test_alias':'container_test_AnnotatedComponent',
            'container_test_alias2':'container_test_AnnotatedSubComponent',
        },
    }
    cont = GetGlobalContainer(config)
    test = cont.get('container_test_alias')
    assert isinstance(test, TstAnnotatedComponent)
    assert isinstance(test.test, TstAnnotatedSubComponent)
