config = {
    'container': {
        'components': {
            'webapp2.WSGIApplication': {
                'class': 'webapp2.WSGIApplication',
                'construct_args': {
                    'routes': { 'config': 'mvc:router:routings' },
                }
            },
            'rindow.bridge.google.appengine.jinja2.DefaultEnvironment': {
                'class': 'jinja2.Environment',
                'construct_args': {
                    'loader': { 'ref': 'rindow.bridge.google.appengine.jinja2.DefaultFileSystemLoader' },
                    'extensions': { 'value': ['jinja2.ext.autoescape'] },
                    'autoescape': { 'value': True }
                }
            },
            'rindow.bridge.google.appengine.jinja2.DefaultFileSystemLoader': {
                'class': 'jinja2.FileSystemLoader',
                'construct_args': {
                    'searchpath': { 'config': 'mvc:view:template_paths' }
                }
            }
        }
    }
}
def getConfig():
    return config
