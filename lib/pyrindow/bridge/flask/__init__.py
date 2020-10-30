import flask
from flask.views import MethodView
from flask import Blueprint
from importlib import import_module

config = {
    'container': {
        'aliases': {
            'flask_caching.cacheDriver':'pyrindow.stdlib.lrucache.LruCache',
        },
        'components': {
            'flask.Flask': {
                'factory': 'pyrindow.bridge.flask.FlaskFactory',
                'class': 'flask.Flask',
                'factory_args': {
                    'params': { 'import_name': __name__ },
                    'config': { 'config':'flask.config' },
                }
            },
            'flask_caching.Cache': {
                'class': 'flask_caching.Cache',
                'construct_args': {
                    'config': {'config': 'flask:flask_caching:config'}
                }
            },
            'flask_login.LoginManager': {
                'class': 'flask_login.LoginManager',
            },
            'flask_wtf.csrf.CSRFProtect': {
                'class': 'flask_wtf.csrf.CSRFProtect',
            },
            'pyrindow.stdlib.lrucache.LruCache': {
                'class': 'pyrindow.stdlib.lrucache.LruCache',
            },
        }
    },
    'flask': {
        'config': {
        },
        'jinja_options': {
            'extensions': {
                'jinja2.ext.autoescape':True,
            },
            #'bytecode_cache':'pyrindow.cms.pages.template.FileSystemBytecodeCache',
        },
        #'secret_key': '__secret_key__',
        'flask_caching': {
            'enable': False,
            'name':'flask_caching.Cache',
            'config': {
                "CACHE_TYPE": "pyrindow.bridge.flask.flask_caching.lrucache",
                #"CACHE_THRESHOLD": 500,
                #"CACHE_IGNORE_ERRORS": False,
                #"CACHE_DEFAULT_TIMEOUT": 300,
            }
        },
        'flask_login': {
            #'enable': False,
            'name':'flask_login.LoginManager',
            #'login_view':'view_name'
            #'user_loader':'loader_name'
        },
        'flask_wtf.csrf': {
            #'enable': False,
            'name':'flask_wtf.csrf.CSRFProtect',
        },
    },
}
def getConfig():
    return config

def FlaskFactory(serviceLocator,**kwargs):
    params = kwargs.get('params')
    app = flask.Flask(**params)
    app.config['serviceLocator'] = serviceLocator
    flask_configs = serviceLocator.get('config').get('flask')
    if flask_configs:
        secret_key = flask_configs.get('secret_key')
        if secret_key:
            app.secret_key = secret_key
        jinja_options = flask_configs.get('jinja_options')
        if jinja_options:
            for name,value in jinja_options.items():
                if name in ['loader','bytecode_cache']:
                    value = serviceLocator.get(value)
                    app.jinja_options[name] = value
                elif name in ['extensions']:
                    if app.jinja_options.get(name)==None:
                        app.jinja_options[name] = []
                    for n,v in value.items():
                        if v:
                            if not n in app.jinja_options[name]:
                                app.jinja_options[name].append(n)
                else:
                    app.jinja_options[name] = value
        flask_caching = flask_configs.get('flask_caching')
        if flask_caching and flask_caching.get('enable'):
            cache = serviceLocator.get(flask_caching.get('name'))
            cache.init_app(app)
        flask_login = flask_configs.get('flask_login')
        if flask_login and flask_login.get('enable'):
            login = serviceLocator.get(flask_login.get('name'))
            if flask_login.get('login_view'):
                login.login_view = flask_login.get('login_view')
            login.init_app(app)
            if flask_login.get('user_loader'):
                loader = getCallable(serviceLocator,flask_login.get('user_loader'))
                @login.user_loader
                def user_loader(user_id):
                    return loader(user_id)
        flask_wtf_csrf = flask_configs.get('flask_wtf.csrf')
        if flask_wtf_csrf and flask_wtf_csrf.get('enable'):
            csrf = serviceLocator.get(flask_wtf_csrf.get('name'))
            csrf.init_app(app)
    # Load default config and override config from an environment variable
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)
    routings = []
    controllers = []
    mvc = serviceLocator.get('config').get('mvc')
    if mvc and isinstance(mvc,dict):
        router = mvc.get('router')
        if router and isinstance(router,dict):
            r = router.get('routings')
            if(r):
                routings = r
            r = router.get('controllers')
            if(r):
                controllers = r
        flaskconfig = mvc.get('config')
        if flaskconfig and isinstance(flaskconfig,dict):
            app.config.update(flaskconfig)
    for route in routings:
        path,handler,name = route
        strHandler = None
        if(isinstance(handler,str)):
            strHandler = handler
            handler = getObject(handler)
        if(isinstance(handler,MethodView)):
            app.add_url_rule(path, view_func=handler.as_view(name))
        else:
            if(isinstance(strHandler,str)):
                raise Exception('Invalid handler type: '+strHandler)
            else:
                raise Exception('Invalid handler type for :'+path)
    for handler in controllers:
        strHandler = None
        if(isinstance(handler,str)):
            strHandler = handler
            handler = getObject(handler)
        if(isinstance(handler,Blueprint)):
            app.register_blueprint(handler)
        else:
            if(isinstance(strHandler,str)):
                raise Exception('Invalid handler type: '+strHandler)
            else:
                raise Exception('Invalid blueprint handler type')
    return app

def getCallable(serviceLocator,component):
    if isinstance(component,str):
        loader = serviceLocator.get(component)
    elif isinstance(component,tuple):
        componentName,method = component
        loaderComponent = serviceLocator.get(componentName)
        loader = getattr(loaderComponent,method)
    else:
        raise Exception('Invalid component name type')
    return loader

def getObject(fullName):
    idx = fullName.rfind('.')
    if(idx>0):
        moduleName = fullName[0:idx]
        className = fullName[idx+1:]
    else:
        moduleName = fullName
        className = fullName
    module = import_module(moduleName)
    return getattr(module,className)

url_maps = []

def route(name,filename,**kwargs):
    annotation = flask.Blueprint(name, filename, **kwargs)
    url_maps.add(annotation)
    return annotation
