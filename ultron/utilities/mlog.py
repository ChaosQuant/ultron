# -*- coding: utf-8 -*-

import threading,logging,datetime,os, six
from ultron.utilities.singleton import Singleton
@six.add_metaclass(Singleton)
class MLog(object):
    
    def __init__(self):
        self._logging = None #self._config(level=logging.DEBUG)
    
    def config(self, name="logging", level=logging.DEBUG):
        self._logging = self._config(name=name, level=level)

    def _config(self, name="logging", level=logging.DEBUG):
        """
        Constructor
        """
        dir_name = os.path.expandvars('$HOME') + '/MLOG/' + name + '/'
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        filename = dir_name + name + '_' + datetime.datetime.now().strftime('%b_%d_%H_%M')+'.log'
        #format_str = "[%(process)d %(thread)d][%(asctime)s][%(filename)s line:%(lineno)d][%(levelname)s] %(message)s"
        format_str = "[%(filename)s line:%(lineno)d][%(levelname)s] %(message)s"
        # define a Handler which writes INFO messages or higher to the sys.stderr
        logging.basicConfig(level=level,
                            format=format_str,
                            datefmt='%m-%d %H:%M',
                            filename=filename,
                            filemode='w')
        console = logging.StreamHandler()
        console.setLevel(level)
        formatter = logging.Formatter(format_str)
        console.setFormatter(formatter)
        # 将定义好的console日志handler添加到root logger
        logging.getLogger('').addHandler(console)
        return logging

    def write(self):
        return self._logging
