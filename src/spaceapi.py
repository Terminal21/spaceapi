from ConfigParser import ConfigParser
import json
import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os
import time
import threading


def telnet(txt):
    try:
        telnet = telnetlib.Telnet('192.168.21.148')
    except:
        logging.error('Cannot connect to display, make sure it is on the '
                      'network with IP 192.168.21.148')
        return
    telnet.write('\n\n'.encode('latin1'))
    telnet.write(chr(0x10).encode('latin1'))
    telnet.write(chr(0).encode('latin1'))
    telnet.write(txt.encode('latin1'))


class SpaceApi(object):

    def __init__(self, config):
    	self.status = dict(api = '0.13',
                  space = None,
                  logo = None,
                  url = None,
                  location = dict(
                      address = None,
                      lon = None,
                      lat = None),
                  contact = dict(
                      email = None,
                      ml = None),
                  state = dict(
                      icon = dict(
                          open = None,
                          closed = None),
                      open = False),
                  issue_report_channels = ['email'])
        self.status['space'] = config.get('space', 'space')
        self.status['logo'] = config.get('space', 'logo')
        self.status['url'] = config.get('space', 'url')
        self.status['location']['address'] = config.get('space', 'address')
        self.status['location']['lon'] = config.getfloat('space', 'lon')
        self.status['location']['lat'] = config.getfloat('space', 'lat')
        self.status['contact']['email'] = config.get('space', 'email')
        self.status['contact']['ml'] = config.get('space', 'ml')
        self.status['state']['icon']['open'] = config.get('space', 'open')
        self.status['state']['icon']['closed'] = config.get('space', 'closed')
        self.fn = config.get('space', 'filename')


    def open(self):
        self.status['state']['open'] = True
        self.update()

    def close(self):
        self.status['state']['open'] = False
        self.update()

    def update(self):
        print 'updating'
        with open(os.path.join('htdocs', self.fn), 'w') as out:
            json.dump(self.status, out)


class SpaceApiHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print 'POST' 
        spaceapi_t21 = SpaceApi(config_t21)
        spaceapi_ebk = SpaceApi(config_ebk)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        status = form.getvalue('status')
        if 'open' in status:
            telnet('SPACE OPEN')
            spaceapi_ebk.open()
            spaceapi_t21.open()
        else:
            telnet('SPACE CLOSED')
            spaceapi_ebk.close()
            spaceapi_t21.close()
        self.respond("""asdf""")

    def do_GET(self):
        self.respond("""geh weg""")

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)


config_t21 = ConfigParser()
config_t21.read('etc/spaceapi.ini')
config_ebk = ConfigParser()
config_ebk.read('etc/spaceapi_ebk.ini')


def run():
    server = HTTPServer(('', 8888), SpaceApiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    while 1:
        pass
        time.sleep(1)

