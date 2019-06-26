# coding=utf-8

import gevent.monkey; gevent.monkey.patch_all()
from twisted.internet import reactor
from ultron.cluster.central.central_engine import CentralEngine
from ultron.utilities.mlog import MLog

if __name__ == "__main__":
    MLog.config('central')
    reactor.__init__()
    central_engine = CentralEngine()
    reactor.run()
