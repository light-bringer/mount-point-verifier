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
  -b pre-backup data status backup, gives back an unique string, save the same
  -p post-backup data status backup, gives back an unique string, save the same
  -v "unique_input_id1,unique_id_2" provided after backups (Pre and Post) with no space in between.
 

  Pass -v/-b/-p one at a time

Example : 
 ## Pre - backup : python mount_point_checker.py -b -m "/path/to/mount1" -m "/path/to/mount2"
 ## Post - backup : python mount_point_checker.py -p -m "/path/to/mount1" -m "/path/to/mount2" 
 ## To verify : python mount_point_checker.py -v "pre_migration_key,post_migration_key" -m "/path/to/mount1" -m "/path/to/mount2"  

"""

import os
import uuid
import datetime
import argparse
import pickle
import hashlib

__BACKUPDIR = '/home/lightbringer/Desktop'
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
            self.__MOUNTDETAILS[hashlib.md5(mount).hexdigest()] = mountdata


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
            print "Error: Not a valid directory, do not have write permission"
            exit(-1)
    except Exception as e:
        print e
        exit(-100)


def main(args):
    '''
    the holy grail main ()
    '''
    mountlist = []
    for mounts in list(args.mount_paths):
        # remove all trailing slashes from path
        mountlist.append(mounts.rstrip(os.sep))
     
    pre_migration = args.b
    post_migration = args.p
    verify = args.uuid
    
    currentMount = MountData(mountlist)

    if pre_migration is True:
        backupdir = os.path.join(__BACKUPDIR, 'pre_migration')
        os.makedirs(backupdir)
        print " ----- Pre Migration Mode ------ "
        if check_write_permission(backupdir) is False:
            print " ===== Backup Path is not writeable ====="
            print " ***** ERROR ***** "
            exit(-1)
        else:
            unique_id = uuid.uuid4().hex
            backupfile = os.path.join(backupdir, unique_id)
            os.makedirs(backupfile)
            backupfile = os.path.join(backupfile, __BACKUPFILEPATH)
            with open(backupfile, 'wb+') as output:
                pickle.dump(currentMount, output)
            print "Backup taken!!"
            print "Please save this unique token for pre-migration: %s"%(unique_id)
            exit(0)
    elif post_migration is True:
        backupdir = os.path.join(__BACKUPDIR, 'post_migration')
        os.makedirs(backupdir)
        print " ----- Post Migration Mode ------ "
        if check_write_permission(backupdir) is False:
            print " ===== Backup Path is not writeable ====="
            print " ***** ERROR ***** "
            exit(-1)
        else:
            unique_id = uuid.uuid4().hex
            backupfile = os.path.join(backupdir, unique_id)
            os.makedirs(backupfile)
            backupfile = os.path.join(backupfile, __BACKUPFILEPATH)
            with open(backupfile, 'wb+') as output:
                pickle.dump(currentMount, output)
            print "Backup taken!!"
            print "Please save this unique token for post-migration : %s"%(unique_id)
            exit(0)
    elif bool(verify) is True:
        uuidstrings = args.uuid
        uuids = uuidstrings.split(',')
        if(len(uuids)!=2):
            print "Give only two unique keys, STRICTLY!"
            exit(-1)
        pre_migrate_uuid, post_migrate_uuid = uuids[0], uuids[1]
        pre_backupdir = backupdir = os.path.join(__BACKUPDIR, 'pre_migration')
        post_backupdir = os.path.join(__BACKUPDIR, 'post_migration')
        backed_up_data_path_pre = os.path.join(pre_backupdir, pre_migrate_uuid)
        backed_up_data_path_pre = os.path.join(backed_up_data_path_pre, __BACKUPFILEPATH)
        backed_up_data_path_post = os.path.join(post_backupdir, post_migrate_uuid)
        backed_up_data_path_post = os.path.join(backed_up_data_path_post, __BACKUPFILEPATH)
        preBackupMount, postBackupMount = None, None
        with open(backed_up_data_path_pre, 'rb') as input:
            preBackupMount = pickle.load(input)
        with open(backed_up_data_path_post, 'rb') as input:
            postBackupMount = pickle.load(input)
        if compare(preBackupMount, postBackupMount):
            print " *** Consistent data *** "
            exit(0)
        else:
            print " *** Inconsistent Data *** "
            return(100)
    
    return


if __name__ == '__main__':
    helpstr = """
    PROGRAM : mount_point_checker.py
    PyVersion : Python 2.7
    This module takes multiple mount paths and compares them after backup
    The module has 2 modes : Backup (-b) and Verify (-v)

    Input Params : 
    -m <mount_points> All the mount point data that need to be backed up, 
            can be multiple, in that case please use multiple -m params
    -b pre-backup data status backup, gives back an unique string, save the same
    -p post-backup data status backup, gives back an unique string, save the same
    -v "unique_input_id1,unique_id_2" provided after backups (Pre and Post) with no space in between.
    

    Pass -v/-b/-p one at a time

    Example : 
    ## Pre - backup : python mount_point_checker.py -b -m "/path/to/mount1" -m "/path/to/mount2"
    ## Post - backup : python mount_point_checker.py -p -m "/path/to/mount1" -m "/path/to/mount2" 
    ## To verify : python mount_point_checker.py -v "pre_migration_key,post_migration_key" -m "/path/to/mount1" -m "/path/to/mount2"  

    """
    Parser = argparse.ArgumentParser()
    Parser.add_argument('-m', dest='mount_paths', help=helpstr, default=[],
                        type=str, action='append', required=True)
    Parser.add_argument('-b', action='store_true')
    Parser.add_argument('-p', action='store_true')
    Parser.add_argument('-v', dest='uuid', action='store')
    Parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args, leftovers = Parser.parse_known_args()
    if (bool(args.b)*bool(args.p)*bool(args.uuid)) is True:
        print "Error: Give either -b or -v option"
        print "-b : Take Backup"
        print "-v <backup_id> Verify from backup"
        exit(-1)
    parseresults = Parser.parse_args()
    main(parseresults)


