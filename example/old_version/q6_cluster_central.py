# coding=utf-8

import sys
import gevent.monkey; gevent.monkey.patch_all()
from twisted.internet import reactor
sys.path.append('../..')
from ultron.cluster.central.central_engine import CentralEngine

if __name__ == "__main__":
    reactor.__init__()
    central_engine = CentralEngine(host='47.95.193.202',
                        port=6378,
                        pwd='12345678dx')
    reactor.run()
