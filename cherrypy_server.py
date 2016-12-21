from collections import defaultdict
import json
import os
import cherrypy


def get_mp3_info(folder):
    obj = defaultdict(list)
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith('.mp3'):
                obj[root.rsplit('\\')[-1]].append(f)
    return json.dumps(obj)


class AudioServer(object):
    @cherrypy.expose
    def krcl(self):
        return get_mp3_info('KRCL Radio')

    @cherrypy.expose
    def kxci(self):
        return get_mp3_info('KXCI Radio')


if __name__ == '__main__':

    conf = {
        'global': {
            'server.socket_host': '192.168.0.14',
            'server.socket_port': 80
        },
        '/krcl/download': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), 'KRCL Radio'),
            'response.headers.Content-Disposition': 'attachment'
        },
        '/krcl/stream': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), 'KRCL Radio')
        },
        '/kxci/download': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), 'KXCI Radio'),
            'response.headers.Content-Disposition': 'attachment'
        },
        '/kxci/stream': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), 'KXCI Radio')
        }
    }

    cherrypy.quickstart(AudioServer(), '/', conf)
