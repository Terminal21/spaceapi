from ConfigParser import ConfigParser
import json
import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os
import time
import threading
import telnetlib
import paho.mqtt.client as mqtt

def telnet(txt):
    try:
        telnet = telnetlib.Telnet('192.168.21.148')
    except:
        print('Cannot connect to display, make sure it is on the '
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

config_t21 = ConfigParser()
config_t21.read('etc/spaceapi.ini')
config_ebk = ConfigParser()
config_ebk.read('etc/spaceapi_ebk.ini')

T21 = SpaceApi(config_t21)
EBK = SpaceApi(config_ebk)


class SpaceApiHandler(BaseHTTPRequestHandler):
    """currently no-op, can go away if spacemaster doesnt send http requests anymore"""


    def do_POST(self):
        self.respond("""asdf""")

    def do_GET(self):
        self.respond("""geh weg""")

    def respond(self, response, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(response))
        self.end_headers()
        self.wfile.write(response)


def get_last_pl():
    with open('.lastpl', 'r') as last_pl:
        return last_pl.read().strip()

def set_last_pl(pl):
    with open('.lastpl', 'w') as last_pl:
        last_pl.write(pl)

def mqtt_received(client, data, message):
    payload = message.payload.decode('utf8')
    if payload == get_last_pl():
        return
    if payload == 'true':
        T21.open()
        EBK.open()
        telnet('SPACE OPEN')
    elif payload == 'false':
        T21.close()
        EBK.close()
        telnet('SPACE CLOSED')
    set_last_pl(payload)


def run():
    server = HTTPServer(('', 8888), SpaceApiHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    mqttc = mqtt.Client()
    mqttc.connect('localhost')
    time.sleep(1)
    mqttc.subscribe('space/status/open')
    mqttc.on_message = mqtt_received
    mqttc.loop_start()
    while 1:
        pass
        time.sleep(1)

