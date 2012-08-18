from cherrypy import wsgiserver

def my_crazy_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return ['Hello world!']

server = wsgiserver.CherryPyWSGIServer(
            ('0.0.0.0', 8080), my_crazy_app,
            server_name='test.hagreve.com')
server.start()

