# coding=utf-8

import sys
import gevent.monkey; gevent.monkey.patch_all()
from twisted.internet import reactor
sys.path.append('../..')
from ultron.cluster.work.work_engine import WorkEngine

if __name__ == "__main__":
    reactor.__init__()
    work_engine = WorkEngine()
    reactor.run()
