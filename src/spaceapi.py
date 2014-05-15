from ConfigParser import ConfigParser
from threading import Thread
import json
import logging
import os
import time
import zmq

class SpaceApi(object):

    status = dict(version = '0.13',
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
                      open = False))

    def __init__(self, config):
        self.status['space'] = config.get('space', 'space')
        self.status['logo'] = config.get('space', 'logo')
        self.status['url'] = config.get('space', 'url')
        self.status['location']['address'] = config.get('space', 'address')
        self.status['location']['lon'] = config.get('space', 'lon')
        self.status['location']['lat'] = config.get('space', 'lat')
        self.status['contact']['email'] = config.get('space', 'email')
        self.status['contact']['ml'] = config.get('space', 'ml')

        publisher = config.get('zeromq', 'publisher')

        self.spacemrescvr = SpaceMessageRecvr(self, publisher)
        self.spacemrescvr.start()

    def update(self, spacemessage):
        if 'spaceopen' in spacemessage:
            self.status['state']['open'] = bool(spacemessage['spaceopen'])
            with open(os.path.join('htdocs', 'status.json'), 'w') as out:
                json.dump(self.status, out)

    def serve_forever(self):
        logging.info('SpaceAPI started')
        while True:
            time.sleep(600)
            logging.info('SpaceAPI hartbeat')


class SpaceMessageRecvr(Thread):

    _continue = True

    def __init__(self, listener, publisher):
        Thread.__init__(self) 
        self.daemon = True

        logging.debug('SpaceMessageRecvr initialized')
        self.listener = listener

        zcontext = zmq.Context()
        self.subscriber = zcontext.socket(zmq.SUB)
        self.subscriber.connect(publisher)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, '')

    def run(self):
        logging.info('starting zeromq subscription')
        while self._continue:
            try:
                message = self.subscriber.recv_json()
                logging.info('receving zeromq message {}'.format(str(message)))
                self.listener.update(message)
            except Exception as e:
                logging.error(e)

    def stop(self):
        self.__continue = False
        self.subscriber.close()
        logging.info('stopping zeromq subscription')

def run():
    logformat = "%(asctime)s %(levelname)s [%(name)s][%(threadName)s] %(message)s"
    logging.basicConfig(format=logformat, level=logging.DEBUG)

    config = ConfigParser()
    config.read('etc/spaceapi.ini')

    spaceapi = SpaceApi(config)
    spaceapi.serve_forever()
