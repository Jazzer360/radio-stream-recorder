import json
import os
import cherrypy


def make_app(folder, rel_url):
    app = ProgramList(folder)
    conf = {}
    conf['/download'] = {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': folder,
        'response.headers.Content-Disposition': 'attachment'
    }
    conf['/stream'] = {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': folder,
        'response.stream': True,
    }
    return (app, rel_url, conf)


class ProgramList(object):
    def __init__(self, root_folder):
        self.root_folder = root_folder

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1:
            cherrypy.request.params['program'] = vpath.pop()
            return self
        return vpath

    @cherrypy.expose
    def index(self, program=None):
        if program:
            print program
            folder = os.path.join(self.root_folder, program)
            resp = [name for name in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, name)) and
                    name.endswith('.mp3')]
        else:
            resp = [name for name in os.listdir(self.root_folder)
                    if os.path.isdir(os.path.join(self.root_folder, name))]
        return json.dumps(resp)


if __name__ == '__main__':

    cherrypy.config.update(
        {
            'server.socket_host': '192.168.0.14',
            'server.socket_port': 8800
        })

    cherrypy.tree.mount(*make_app('D:\\Radio Podcasts\\KRCL Radio', '/krcl'))

    cherrypy.engine.start()
    cherrypy.engine.block()
