#!/usr/bin/python3
import configparser
import argparse
import sys
import shutil
import os

from ftplib import FTP
from datetime import date

CWD = os.getcwd()
parser = argparse.ArgumentParser()
parser.add_argument('--directory-name', help='Directory to back up', metavar='FILENAME')

print("\nabbackup 0.0.1: A backup tool (http://www.github.com/arkabytes/abbackup)")
args = parser.parse_args()

if len(sys.argv) == 1:
    print("No arguments provided. Execute '" + sys.argv[0] + " -h' for help")
    exit()

if args.directory_name:

    backup_filename = args.directory_name + '_' + str(date.today())
    # Create zip file from directory
    shutil.make_archive(backup_filename, 'zip', args.directory_name)

    # Reading config file to connect to FTP server
    config = configparser.ConfigParser()
    config.sections()
    config.read('abbackup.conf')

    # Reading config information about ftp connection
    host = config['ftp_server']['host']
    port = config['ftp_server']['port']
    username = config['ftp_server']['username']
    password = config['ftp_server']['password']

    # Connect to ftp server and upload backup file
    ftp = FTP(host, username, password)
    print('Login ok')
    print('Uploading file . . .')
    ftp.storbinary('STOR ' + backup_filename + '.zip', open(backup_filename + '.zip', 'rb'))
    print("Quitting . . .")
    ftp.quit()
    print('Bye')
