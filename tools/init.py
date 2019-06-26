from ultron.config import config_setting

config_setting.set_queue(qtype='redis', host='180.166.26.82',
                        port=4430, pwd='12345678dx', db=1)
config_setting.update()