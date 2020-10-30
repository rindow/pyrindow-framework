import os, jinja2
from pyrindow.container.module_manager import ModuleManager
from flask import render_template, request, url_for, redirect, current_app
from flask_login import login_required, login_user, UserMixin, current_user


class User(UserMixin):
    pass


def user_loader(user_id):
    user = User()
    user.id = user_id
    return user


def test_tiny_flask():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'foo': 'bar',
        'flask': {
            'secret_key': 'test secret key',
            'config': {
                'some_option': 'some_value',
            },
        },
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    assert 'pyrindow.bridge.flask'==app.name
    app.testing = True
    @app.route('/')
    def hello():
        return 'Hello!'
    client = app.test_client()
    rv = client.get('/')
    assert '200 OK'==rv.status
    assert b'Hello!'==rv.data
    assert 'bar'==app.config['service_locator'].get('config')['foo']
    assert 'test secret key'==app.secret_key
    assert 'some_value'==app.config['some_option']

def test_blueprint():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'container': {
            'components': {
                'tests.flask.tst_blueprint': {
                    'class': 'tests.flask.tst_blueprint',
                    'factory_mode': 'import',
                    'properties': {
                        'service_locator': ('ref', 'ServiceLocator'),
                    },
                },
            },
        },
        'mvc': {
            'router': {
                'controllers': {
                    'tests.flask.tst_blueprint': (True, 'route')
                },
            },
        },
        'foo': 'bar'
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    app.testing = True
    assert 'pyrindow.bridge.flask'==app.name
    client = app.test_client()
    rv = client.get('/sub/hello')
    assert '200 OK'==rv.status
    assert b'hello bar in sub module!'==rv.data

def test_command():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'container': {
            'components': {
                'tst_command': {
                    'class': 'tests.flask.tst_command',
                    'factory_mode': 'import',
                },
            },
        },
        'console': {
            'commands': {
                __name__: {
                    'test-command1': {
                        'component': ('tst_command','exec_test_commnad1'),
                    },
                    'test-command2': {
                        'component': ('tests.flask.tst_command','exec_test_commnad2'),
                        'factory_mode': 'import'
                    },
                    'test-command3': {
                        'component': 'tests.flask.tst_command.exec_test_commnad3',
                        'factory_mode': 'import'
                    },
                },
            },
        },
        'foo': 'bar'
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    app.testing = True
    assert 'pyrindow.bridge.flask'==app.name
    runner = app.test_cli_runner()
    result = runner.invoke(args=['tst-command1'])
    assert 'Test Command' in result.output
    result = runner.invoke(args=['tst-command2'])
    assert 'Test Command' in result.output
    result = runner.invoke(args=['tst-command3'])
    assert 'Test Command' in result.output


def test_jinja_options():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'flask': {
            'jinja_options': {
                'loader': 'testLoader',
                'bytecode_cache': 'jinja2.MemcachedBytecodeCache',
                'extensions': {
                    'jinja2.ext.debug': True,
                },
            },
        },
        'container': {
            'components': {
                'testLoader': {
                    'class': 'jinja2.FileSystemLoader',
                    'construct_args': {
                        'searchpath': ('value', os.path.dirname(__file__) + '/views/jinja_options')
                    },
                },
            },
        },
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    app.testing = True
    assert 'pyrindow.bridge.flask'==app.name
    @app.route('/')
    def hello():
        return render_template('test_jinja_options.html')
    client = app.test_client()
    rv = client.get('/')
    assert '200 OK', rv.status
    assert b'template test_jinja_options', rv.data
    assert isinstance(
        app.jinja_env.bytecode_cache,
        jinja2.MemcachedBytecodeCache)
    assert isinstance(
        app.jinja_env.extensions['jinja2.ext.DebugExtension'],
        jinja2.ext.DebugExtension)

def test_flask_caching():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'flask': {
            'params': {
                'import_name': __name__
            },
            'flask_caching': {
                'enable': True,
            },
        },
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    app.testing = True

    #assert app.jinja_env.loader.searchpath==[]
    #if app.jinja_env.loader.searchpath!=[]:
    #    raise Exception('loader error')
    @app.route('/')
    def hello():
        return render_template('hellocaching.html')
    client = app.test_client()
    rv = client.get('/')
    assert '200 OK'==rv.status
    assert b'Hello caching template'==rv.data
    cache = module_manager.get_service_locator().get('pyrindow.stdlib.lrucache.LruCache')
    assert 1==len(cache)

def test_flask_login():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'container': {
            'components': {
                'test_user_loader': {
                    'class': 'tests.flask.flask_test.user_loader',
                    'factory_mode': 'property',
                },
            },
        },
        'flask': {
            'secret_key': 'test secret key',
            'params': {
                'import_name': __name__
            },
            'flask_login': {
                'enable': True,
                'login_view': 'login',
                'user_loader':'test_user_loader',
            },
        },
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    assert 'tests.flask.flask_test'==app.name
    app.testing = True
    @app.route('/')
    @login_required
    def hello():
        return 'Hello %s!' % current_user.get_id()
    @app.route('/login',methods=['GET','POST'])
    def login():
        if request.method == 'GET':
            return 'some login form'
        username = request.form.get('username')
        if username!='admin':
            return 'login failed'
        login_user(user_loader(username))
        return redirect(url_for('hello'))
    client = app.test_client()
    rv = client.get('/')
    assert '302 FOUND'==rv.status
    assert 'http://localhost/login?next=%2F'==rv.headers['Location']
    rv = client.get('/login?next=%2F')
    assert '200 OK'==rv.status
    assert b'some login form'==rv.data
    rv = client.post('/login', data={'username': 'admin'})
    assert '302 FOUND'==rv.status
    assert 'http://localhost/'==rv.headers['Location']
    rv = client.get('/')
    assert '200 OK'==rv.status
    assert b'Hello admin!'==rv.data

def test_flask_wtf_csrf():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'flask': {
            'secret_key': 'test secret key',
            'params': {
                'import_name': __name__
            },
            'flask_wtf.csrf': {
                'enable': True,
            },
        },
    }
    # assert 'tests.flask.flask_test'==__name__
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    assert 'tests.flask.flask_test'==app.name
    app.testing = True
    assert 'tests.flask.flask_test'==app.import_name
    assert 'tests.flask.flask_test'==app.name
    assert ['C:\\Users\\yuichi\\Documents\\WebDev\\pyrindow\\pyrindow-framework\\tests\\flask\\templates']==app.jinja_loader.searchpath
    # assert 'tests.flask.flask_test'==app.template_folder
    # assert 'tests.flask.flask_test'==app.root_path
    @app.route('/',methods=['GET','POST'])
    def hello():
        if request.method == 'GET':
            return render_template('csrf_form.html')
        return 'Hello !'
    client = app.test_client()
    rv = client.get('/')
    assert '200 OK'==rv.status
    csrf_token = rv.data
    rv = client.post('/', data={'foo': 'bar'})
    assert '400 BAD REQUEST'==rv.status
    rv = client.post('/', data={'csrf_token': csrf_token})
    assert '200 OK'==rv.status
    assert b'Hello !'==rv.data


def test_flask_sqlalchemy():
    config = {
        'module_manager': {
            'modules': {
                'pyrindow.bridge.flask': True,
            },
        },
        'flask': {
            'secret_key': 'test secret key',
            'params': {
                'import_name': __name__
            },
            'flask_sqlalchemy': {
                'enable': True,
                'database_uri': 'sqlite:///:memory:',
                'save_settings_to': 'tests.flask.tst_config.db',
            },
        },
    }
    module_manager = ModuleManager(config)
    app = module_manager.get_service_locator().get('flask.Flask')
    assert 'tests.flask.flask_test'==app.name
    db = module_manager.get_service_locator().get('flask_sqlalchemy.SQLAlchemy')
    from . import tst_entities
    app.testing = True
    with app.app_context():
        db.create_all()
    with app.app_context():
        post = tst_entities.Post(title='title',body='body')
        db.session.add(post)
        db.session.commit()
    with app.app_context():
        post = tst_entities.Post.query.filter_by(id=1).first()
        assert post.title == 'title'
        assert post.body == 'body'
