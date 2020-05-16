config = {
    'container': {
        'components': {
            'flask.Flask': {
                'factory': 'rindow.bridge.flask.FlaskFactory',
                'class': 'flask.Flask',
                'factory_args': {
                    'params': { 'import_name': __name__ },
                    'config': 'mvc',
                }
            }
        }
    }
}
def getConfig():
    return config

import flask
def FlaskFactory(serviceLocator,**kwargs):
    params = kwargs.get('params')
    app = flask.Flask(**params)
    routings = []
    mvc = serviceLocator.get('config').get('mvc')
    if mvc and isinstance(mvc,dict):
        router = mvc.get('router')
        if router and isinstance(router,dict):
            routings = router.get('routings')
        flaskconfig = mvc.get('config')
        if flaskconfig and isinstance(flaskconfig,dict):
            app.config.update(flaskconfig)
    for route in routings:
        path,handler,name = route
        app.add_url_rule(path, view_func=handler.as_view(name))
    app.config['serviceLocator'] = serviceLocator
    # Load default config and override config from an environment variable
    app.config.from_envvar('FLASKR_SETTINGS', silent=True)
    return app
