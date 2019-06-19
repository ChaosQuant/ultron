# -*- coding: utf-8 -*-
import pdb
import json
import base64
import os
import shutil
from ultron.utilities.short_uuid import uuid, decode
from ultron.cluster.work.extern_modules.base_module import BaseModule
from ultron.utilities.zlib_engine import unzip_compress

class Module(BaseModule):
    def __init__(self, name, wid, token, redis_client):
        super(Module, self).__init__(name, wid, token, redis_client)
        self._func = {'upload_packet':self.upload_packet}
        self._namespace = 'packet'
        
    def process_respone(self, result):
        name = result['name']
        opcode = result['opcode']
        self._func[opcode](result)
    
    def upload_packet(self, result):
        uid = result['uid']
        dir_name = './'
        file_info = bytes(result['file_info'], encoding='utf-8')
        packet_name = result['packet_name']
        file_name = result['file_name']
        all_dir_name = os.path.join(dir_name, str(uid))
        file_list = []
        if not os.path.exists(all_dir_name):
            os.makedirs(all_dir_name)
        file_content = base64.b64decode(file_info)
        
        #检查目录是否存在
        if os.path.exists(os.path.join(all_dir_name, str(packet_name))):
            shutil.rmtree(os.path.join(all_dir_name, str(packet_name)))
        
        #重新创建
        os.mkdir(os.path.join(all_dir_name, str(packet_name)))
            
        #保存成文件
        new_file = os.path.join(all_dir_name, str(packet_name), file_name)
        with open(new_file, 'wb') as f:
            f.write(file_content)
        unzip_compress(new_file, os.path.join(all_dir_name, str(packet_name)))
        if os.path.isfile(new_file):
            os.remove(new_file)
                
        ## 通知主节点发布成功，进行启动
        packet_info = {'name':'tasks','opcode':'startup_task', 'dir_name':all_dir_name,
                       'wid':self._wid,'work_name': packet_name,'token':self._token}
        self._redis_client.hset('ultron:work:ctask', uuid(), json.dumps(packet_info))
        
