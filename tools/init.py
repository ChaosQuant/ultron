from ultron.config import config_setting

config_setting.set_queue(qtype='redis', host='172.17.0.1',
                        port=4430, pwd='12345678dx', db=1)
config_setting.update()
