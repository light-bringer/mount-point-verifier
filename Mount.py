#!/usr/bin/env python2
# -*- coding: utf-8 -*-


class MountInfo():
    '''
    Class to generate mount path info
    '''

    def __init__(self, mount_path):
        self.__UUID = str(uuid.uuid4())
        self.__DATE = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.__MOUNTPATH = mount_path
        self.__ALLFILES, self.__COMMONPREFIX = read_dir(mount_path)
        self.__RELATIVEPATHS = relative_paths(self.__ALLFILES, self.__COMMONPREFIX)
        self._FILESIZES = get_filesizes(self.__ALLFILES, self.__COMMONPREFIX)

    def gen_dict(self):
        Dict = {}
        Dict['uuid'] = self.__UUID
        Dict['date'] = self.__DATE
        Dict['mountpath'] = self.__MOUNTPATH
        Dict['allfiles'] = self.__ALLFILES
        Dict['relative'] = self.__RELATIVEPATHS
        Dict['filesizes'] = self.__RELATIVEPATHS

        return Dict



class MountData():
    def __init__(self, mountpaths):
        self.__id = uuid.uuid4().hex
        self.__MOUNTPOINTS = mountpaths
        self.__MOUNTDETAILS = {}
        self.generate_mountdata()


    def generate_mountdata(self):
        for mount in self.__MOUNTPOINTS:
            mountdata = MountInfo(mount)
            self.__MOUNTDETAILS[hashlib.md5(mount).hexdigest()] = mountdata


    def get_uuid(self):
        return self.__id

    def get_mountdata(self):
        return self.__MOUNTDETAILS

