# mount-point_verifier

PROGRAM : mount_point_checker.py

PyVersion : Python 2.7

This module takes multiple mount paths and compares them after backup
The module has 2 modes : Backup (-b) and Verify (-v)

Input Params :
  -m <mount_points> All the mount point data that need to be backed up,
        can be multiple, in that case please use multiple -m params.
  -d </path/to/backup/directory> Path where the backup will be created/stored. (Required)
  -v "unique_input_id" provided after backup. (Optional)
  -b use this param to backup for the first time,
        will generate a unique ID String that you need to keep for verification (Optional).

Example : 
 ## To backup : python mount_point_checker.py -b -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir"
 ## To verify : python mount_point_checker.py -m "/path/to/mount1" -m "/path/to/mount2" -d "/path/to/backup/dir" -v "6b686ff2d15f492486b1148f1083f2e0"

