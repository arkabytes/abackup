#!/usr/bin/python3
import configparser
import argparse
import ftplib
import sys
import shutil
import os
import smtplib
import socket
import logging

from email.mime.text import MIMEText
from email.errors import MessageError
from ftplib import FTP
from datetime import date


CWD = os.getcwd()
CONFIG_FILE = 'abbackup.conf'
CONFIG_FTP_SECTION = 'ftp_server'
CONFIG_EMAIL_SECTION = 'email_settings'
CONFIG_BACKUP_SECTION = 'backup'
OPTION_HOST = 'host'
OPTION_PORT = 'port'
OPTION_USERNAME = 'username'
OPTION_PASSWORD = 'password'
OPTION_SUBJECT = 'subject'
OPTION_FROM = 'from'
OPTION_TO = 'to'
OPTION_BODY = 'body'
OPTION_BACKUP_NAME = 'name'

LOG_FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
# Initialize logging system
logging.basicConfig(filename='abbackup.log', format=LOG_FORMAT, level=logging.INFO)


def log(message, severity, backup_name, backup_file):
    extra_data = {'backup_name': backup_name, 'backup_file': backup_file}
    if severity == 'warning':
        logging.warning(message, extra=extra_data)
    if severity == 'error':
        logging.error(message, extra=extra_data)
    if severity == 'info':
        logging.info(message, extra=extra_data)


def send_email(email_body, email_subject, email_from, email_to):
    message = MIMEText(email_body)
    message['Subject'] = email_subject
    message['From'] = email_from
    message['To'] = email_to

    print("Sending email notification . . .")
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(email_from, [email_to], message.as_string())
    print("Email sent successfully")
    smtp.quit()


parser = argparse.ArgumentParser()
parser.add_argument('--directory-name', help='Directory to back up', metavar='DIRECTORY_NAME')
parser.add_argument('--name', help='Backup name', metavar='NAME')
parser.add_argument('--email', help='E-mail address where notify operations', metavar='EMAIL_ADDRESS')
parser.add_argument('--list-backups', help='List backups (all or for an specific name)', metavar="[BACKUP_NAME]")

print("\nabbackup 0.1: A backup tool (http://www.github.com/arkabytes/abbackup)")
args = parser.parse_args()

# Check if user has provided at least 1 argument (directory to make backup)
if len(sys.argv) == 1:
    print("No arguments provided. Execute '" + sys.argv[0] + " -h' for help")
    exit()

# Check if config file exists
if not os.path.isfile(CONFIG_FILE):
    print("No config file. You must to create it to provide FTP server configuration")
    exit()

if args.directory_name:

    ''' Config file checking '''
    # Reading config file to connect to FTP server
    config = configparser.ConfigParser()
    config.sections()
    config.read('abbackup.conf')

    # Check if config file has the proper section
    if not config.has_section(CONFIG_FTP_SECTION):
        print("Invalid config file (no '" + CONFIG_FTP_SECTION + "' section)")
        print("Exiting . . .")
        exit()

    # Check if config file provided all the needed information to connect to the FTP server
    if not config.has_option(CONFIG_FTP_SECTION, OPTION_HOST) or \
            not config.has_option(CONFIG_FTP_SECTION, OPTION_PORT) or \
            not config.has_option(CONFIG_FTP_SECTION, OPTION_USERNAME) or \
            not config.has_option(CONFIG_FTP_SECTION, OPTION_PASSWORD):
        print("Invalid config file (check syntax)")
        print("Exiting . . .")
        exit()

    # Reading config information about ftp connection
    host = config[CONFIG_FTP_SECTION][OPTION_HOST]
    port = config[CONFIG_FTP_SECTION][OPTION_PORT]
    username = config[CONFIG_FTP_SECTION][OPTION_USERNAME]
    password = config[CONFIG_FTP_SECTION][OPTION_PASSWORD]

    backup_name = 'nonamebackup'
    if args.name:
        backup_name = args.name
    else:
        backup_name = config[CONFIG_BACKUP_SECTION][OPTION_BACKUP_NAME]

    email_subject = None
    email_from = None
    email_to = None
    email_body = None
    # Read email config data (email address can have been introduced manually)
    if config.has_section(CONFIG_EMAIL_SECTION):
        email_subject = config[CONFIG_EMAIL_SECTION][OPTION_SUBJECT]
        email_from = config[CONFIG_EMAIL_SECTION][OPTION_FROM]
        if args.email:
            email_to = args.email
        else:
            email_to = config[CONFIG_EMAIL_SECTION][OPTION_TO]
        email_body = config[CONFIG_EMAIL_SECTION][OPTION_BODY]
    else:
        # No email notification
        print("No email provided to notify operations")
        exit()

    backup_filename = 'noname'
    try:
        backup_filename = backup_name + '_' + str(date.today())
        logging.info("Starting new backup %s/%s", backup_name, backup_filename)
        ''' Making backup '''
        # Create zip file from directory
        shutil.make_archive(backup_filename, 'zip', args.directory_name)
        logging.info('Backup file created')

        ''' FTP Connection and upload '''
        # Connect to ftp server and upload backup file
        print("Connecting to FTP server . . .")
        logging.info('Connecting to FTP server')
        ftp = FTP(host, username, password, timeout=5)
        print('Login ok')
        print('Uploading file . . .')
        ftp.storbinary('STOR ' + backup_filename + '.zip', open(backup_filename + '.zip', 'rb'))
        ftp.quit()
        print('File uploaded')
        logging.info('File uploaded successfully')

        # TODO Remove old backup if it has been there during more than the specified amount of days in config file

        ''' Email notification '''
        send_email(email_body, email_subject, email_from, email_to)
        logging.info('finished backup %s/%s', backup_name, backup_filename)
    except ftplib.Error as e:
        print("Error while uploading file")
        logging.error('Error while uploading file')
        send_email('Error while uploading file', email_subject, email_from, email_to)
    except socket.timeout:
        print("FTP connection timeout excedeed")
        logging.error('FTP connection timeout excedeed')
        send_email('FTP connection timeout excedeed', email_subject, email_from, email_to)
    except MessageError:
        print("Error while sending notification error")
        logging.error('Error while sending notification error', 'error')
    except ConnectionRefusedError:
        print("Error while connection with the smtp server")
        logging.error('Error while connection with the smtp server', 'error')
