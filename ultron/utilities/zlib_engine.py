# -*- coding: utf-8 -*-

import os,os.path
import zipfile

def zip_compress(dir_name, zip_filename):
    filelist = []
    if os.path.isfile(dir_name):
        filelist.append(dir_name)
    else :
        for root, dirs, files in os.walk(dir_name):
            for name in files:
                filelist.append(os.path.join(root, name))
          
    zf = zipfile.ZipFile(zip_filename, "w", zipfile.zlib.DEFLATED)
    for tar in filelist:
        arcname = tar[len(dir_name):]
        zf.write(tar,arcname)
    zf.close()

def unzip_compress(zip_filename, unzip_dir):
    if not os.path.exists(unzip_dir): 
        os.mkdir(unzip_dir)
    zfobj = zipfile.ZipFile(zip_filename)
    for name in zfobj.namelist():
        name = name.replace('\\','/')
        if name.endswith('/'):
            os.mkdir(os.path.join(unzip_dir, name))
        else:           
            ext_filename = os.path.join(unzip_dir, name)
            ext_dir= os.path.dirname(ext_filename)
            if not os.path.exists(ext_dir) : 
                os.mkdir(ext_dir)
            outfile = open(ext_filename, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()