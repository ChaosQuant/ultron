# -*- coding: utf-8 -*-
import datetime
import six
from ultron.utilities.singleton import Singleton
from ultron.utilities.mlog import MLog

@six.add_metaclass(Singleton)
class ModelsSingleton(object):
    def __init__(self):
        __str__ = 'ModelsSingleton'
        self._cluster_map = {}
        
    def add_cluster(self, wid, cluster):
        self._cluster_map[wid] = cluster
    
    def verify_auth_token(self, wid, token):
        _token = None
        if wid in self._cluster_map:
            _token = self._cluster_map[wid]['token']
        return True if (token == _token and _token is not None and token is not None) else False
    
    def check_alive(self, wid):
        now_time = datetime.datetime.now()
        if wid in self._cluster_map:
            last_time = self._cluster_map[wid]['updatime']
        return True if ((now_time - last_time).seconds > 100) else False
    
    def set_alive(self, wid):
        now_time = datetime.datetime.now()
        if wid in self._cluster_map:
            self._cluster_map[wid]['updatime'] = now_time
            MLog.write().info('wid:%s, now_time:%s' % (str(wid), now_time.strftime('%Y-%m-%d %H:%M:%S')))
            
    
    def get_queue(self, wid):
        return self._cluster_map[wid]['queue_name'] if (wid in self._cluster_map) else None

    def get_all_queue(self):
        queue_list = []
        for wid, cluster in self._cluster_map.items():
            queue_list.append(cluster['queue_name'])
        return queue_list
            
        