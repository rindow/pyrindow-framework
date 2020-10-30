from pyrindow.stdlib.datastructure import dict_replace_recursive
import pytest

def test_updateDict():
    config = {'a':'A','b':'B'}
    dict_replace_recursive(config,{'a':'A2'})
    assert {'a':'A2','b':'B'} == config
    dict_replace_recursive(config,{'a':{'a-31':'A31','a-32':'A32'}})
    assert {'a':{'a-31':'A31','a-32':'A32'},'b':'B'} == config
    dict_replace_recursive(config,{'a':{'a-31':{'a-41':'A-41'}}})
    assert {'a':{'a-31':{'a-41':'A-41'},'a-32':'A32'},'b':'B'} == config
    dict_replace_recursive(config,{'a':'a-51'})
    assert {'a':'a-51','b':'B'} == config

def test_addDict1():
    config = {'a':'A','b':'B'}
    dict_replace_recursive(config,{'c':'C'})
    assert {'a':'A','b':'B','c':'C'} == config
    dict_replace_recursive(config,{'a':{'a-21':'A-21'}})
    dict_replace_recursive(config,{'a':{'a-31':'A-31'}})
    assert {'a':{'a-21':'A-21','a-31':'A-31'},'b':'B','c':'C'} == config

def test_addDict2():
    config = {}
    source = {'a':{'b':'C'}}
    dict_replace_recursive(config,source)
    assert config['a']['b'],source['a']['b']
    assert 'C' == config['a']['b']
    config['a']['b'] = 'D'
    assert 'C' == source['a']['b']

def test_addList1():
    config = {'a':'A','b':'B'}
    dict_replace_recursive(config,{'a':['A2']})
    assert {'a':['A2'],'b':'B'} == config
    dict_replace_recursive(config,{'a':['A3']})
    assert {'a':['A2','A3'],'b':'B'} == config
    dict_replace_recursive(config,{'a':[{'a-41':'A-41','a-42':'A-42'}]})
    assert {'a':['A2','A3',{'a-41':'A-41','a-42':'A-42'}],'b':'B'} == config

def test_addList2():
    config = {}
    source = {'a':['B','C']}
    dict_replace_recursive(config,source)
    assert config['a'] == source['a']
    assert ['B','C'] == config['a']
    config['a'].append('D')
    assert ['B','C'] == source['a']

def test_updateTuple():
    config = {'a':'A','b':'B'}
    dict_replace_recursive(config,{'a':('A-21','A-22')})
    assert {'a':('A-21','A-22'),'b':'B'} == config
    dict_replace_recursive(config,{'a':('A-31')})
    assert {'a':('A-31'),'b':'B'} == config
    dict_replace_recursive(config,{'a':{'a-41':('A-41','A-42')}})
    assert {'a':{'a-41':('A-41','A-42')},'b':'B'} == config
    dict_replace_recursive(config,{'a':{'a-41':('A-51')}})
    assert {'a':{'a-41':('A-51')},'b':'B'} == config

def test_addTuple():
    config = {}
    source = {'a':('B',('C1','C2'))}
    dict_replace_recursive(config,source)
    assert config['a'] == source['a']
    assert ('B',('C1','C2')) == config['a']
    assert 'B' == config['a'][0]
    config['a'] = ('D')
    assert ('B',('C1','C2')) == source['a']


def test_UpdateNoneDict():
    config = {'a':'A','b':'B'}
    with pytest.raises(TypeError):
        dict_replace_recursive(config,['c'])

def test_NoneDictBase():
    config = ['a']
    with pytest.raises(TypeError):
        dict_replace_recursive(config,['b'])
