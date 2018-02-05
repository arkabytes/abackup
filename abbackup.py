#!/usr/bin/python3

from ftplib import FTP
import configparser

config = configparser.ConfigParser()
config.sections()
config.read('abackup.conf')

host = config['ftp_server']['host']
port = config['ftp_server']['port']
username = config['ftp_server']['username']
password = config['ftp_server']['password']

ftp = FTP(host, username, password)
#ftp.login()
print('login ok')
ftp.retrlines('LIST')
ftp.quit()
print('quit ok')
