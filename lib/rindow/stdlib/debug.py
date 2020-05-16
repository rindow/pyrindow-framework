def MakeWsgiDump(message):
    def app(environ, start_response):
        status = '503 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return message
    return app
