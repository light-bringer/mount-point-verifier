#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
PROGRAM : mount_point_checker.py
PyVersion : Python 2.7
This module takes multiple mount paths and compares them after backup
The module has 2 modes : Backup (-b) and Verify (-v)

Input Params : 
  -m <mount_points> All the mount point data that need to be backed up, 
        can be multiple, in that case please use multiple -m params
  -d </path/to/backup/directory> Path where the backup will be created/stored (Required)
  -v "unique_input_id" provided after backup (Optional)
  -b use this param to backup for the first time,
        will generate a unique ID String that you need to keep for verification (Optional)

Example : 
 ## To backup : python mount_point_checker.py -b -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir"
 ## To verify : python mount_point_checker.py -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir" -v "6b686ff2d15f492486b1148f1083f2e0"

"""

import os
import uuid
import datetime
import argparse
import pickle


__BACKUPFILEPATH = 'backup.txt'

def read_dir(path):
    '''
    read a Directory and get all files and their full paths
    input : directory path
    output : list(full filepaths) file prefix paths
    '''
    fullfilepaths = [os.path.join(d, x)
    for d, dirs, files in os.walk(path)
    for x in files]

    return fullfilepaths, os.path.commonprefix(fullfilepaths)


def relative_paths(full_filepaths, common_prefix):
    '''
    read fullfilepaths and get all relative filepaths
    input : fullpaths, common_prefix_path
    output : list(relative_filepaths)
    '''
    relative_paths = [os.path.relpath(path, common_prefix) for path in full_filepaths]
    return relative_paths


def get_filesizes(full_filepaths, common_prefix):
    '''
    get file sizes for each and every element and return the same
    as a directory.
    input : list(full_filepath), common_prefix_path
    return : dict({'relative_path': 'file_size'})
    '''
    fileinfodict = {}
    for path in full_filepaths:
        relative_path = os.path.relpath(path, common_prefix)
        fileinfodict[relative_path] = os.stat(path).st_size
    return fileinfodict




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
            self.__MOUNTDETAILS[mount] = mountdata


    def get_uuid(self):
        return self.__id

    def get_mountdata(self):
        return self.__MOUNTDETAILS



def compare(SrcObj, DestObj):
    '''
    Compare two different objects for comparing backup and current
    input : two Data() objects
    output : Boolean <True/False>
    '''
    for key in SrcObj.get_mountdata().keys():
        try:
            if len(DestObj.get_mountdata()[key].gen_dict()['allfiles']) == len(SrcObj.get_mountdata()[key].gen_dict()['allfiles']):
                if DestObj.get_mountdata()[key].gen_dict()['relative'] == SrcObj.get_mountdata()[key].gen_dict()['relative']:
                    if DestObj.get_mountdata()[key].gen_dict()['filesizes'] == SrcObj.get_mountdata()[key].gen_dict()['filesizes']:
                        return True
            else:
                return False
        
        except KeyError as e:
            print e
            return False



def find_mount_point(path):
    path = os.path.abspath(path)
    while not os.path.ismount(path):
        path = os.path.dirname(path)
    return path


def check_write_permission(srcdir):
    '''
    Copy file permissions from src file to dest file
    '''
    try:
        if os.path.isdir(srcdir):
            return os.access(srcdir, os.W_OK)
        else:
            print "Error: Not a valid directory"
            exit(-1)
    except Exception as e:
        print e
        exit(-100)


def main(args):
    '''
    the holy grail main ()
    '''
    backupdir = str(args.backup_path)
    mountlist = []
    for mounts in list(args.mount_paths):
        # remove all trailing slashes from path
        mountlist.append(mounts.rstrip(os.sep))
     
    takebackupflag = args.b
    backup_id = args.backup_id
    currentMount = MountData(mountlist)

    if takebackupflag is True:
        print " ----- Data Backup Mode ------ "
        if check_write_permission(backupdir) is False:
            print " ===== Backup Path is not writeable ====="
            print " ***** ERROR ***** "
            print " ---- give correct backup path ---- "
            exit(-1)
        else:
            unique_id = uuid.uuid4().hex
            backupfile = os.path.join(backupdir, unique_id)
            os.makedirs(backupfile)
            backupfile = os.path.join(backupfile, __BACKUPFILEPATH)
            with open(backupfile, 'wb+') as output:
                pickle.dump(currentMount, output)
            print "Backup taken!!"
            print "Please save this unique token : %s"%(unique_id)
            exit(0)
    elif backup_id is not None:
        backupMount = None
        backed_up_data_path = os.path.join(backupdir, backup_id)
        backed_up_data_path = os.path.join(backed_up_data_path, __BACKUPFILEPATH)
        with open(backed_up_data_path, 'rb') as input:
            backupMount = pickle.load(input)
            if compare(backupMount, currentMount):
                print " *** Consistent data *** "
                exit(0)
            else:
                print " *** Inconsistent Data *** "
                return(100)
    
    return


if __name__ == '__main__':
    helpstr = '''
        PROGRAM : mount_point_checker.py
        PyVersion : Python 2.7
        This module takes multiple mount paths and compares them after backup
        The module has 2 modes : Backup (-b) and Verify (-v)

        Input Params : 
          -m <mount_points> All the mount point data that need to be backed up, 
                can be multiple, in that case please use multiple -m params.
          -d </path/to/backup/directory> Path where the backup will be created/stored (Required)
          -v "unique_input_id" provided after backup (Optional)
          -b use this param to backup for the first time,
                will generate a unique ID String that you need to keep for verification (Optional)

        Example : 
         ## To backup : python mount_point_checker.py -b -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir"
         ## To verify : python mount_point_checker.py -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir" -v "6b686ff2d15f492486b1148f1083f2e0"

        '''
    Parser = argparse.ArgumentParser()
    Parser.add_argument('-m', dest='mount_paths', help=helpstr, default=[],
                        type=str, action='append', required=True)
    Parser.add_argument('-d', action='store', dest='backup_path',
                        help=helpstr, required=True)
    Parser.add_argument('-b', action='store_true')
    Parser.add_argument('-v', action='store', dest='backup_id')
    Parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args, leftovers = Parser.parse_known_args()
    if args.b is False and args.backup_id is None:
        print "Error: Give either -b or -v option"
        print "-b : Take Backup"
        print "-v <backup_id> Verify from backup"
        exit(-1)
    parseresults = Parser.parse_args()
    main(parseresults)


