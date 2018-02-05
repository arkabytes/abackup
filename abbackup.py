#!/usr/bin/python3
import configparser
import argparse
import sys
import shutil
import os
import smtplib

from email.mime.text import MIMEText
from email.errors import MessageError
from ftplib import FTP
from datetime import date

CWD = os.getcwd()
CONFIG_FILE = 'abbackup.conf'
CONFIG_FTP_SECTION = 'ftp_server'
CONFIG_EMAIL_SECTION = 'email_settings'
OPTION_HOST = 'host'
OPTION_PORT = 'port'
OPTION_USERNAME = 'username'
OPTION_PASSWORD = 'password'
OPTION_SUBJECT = 'subject'
OPTION_FROM = 'from'
OPTION_TO = 'to'
OPTION_BODY = 'body'

parser = argparse.ArgumentParser()
parser.add_argument('--directory-name', help='Directory to back up', metavar='DIRECTORY_NAME')
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

    ## Config file checking
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

    ## Making backup ##
    backup_filename = args.directory_name + '_' + str(date.today())
    # Create zip file from directory
    shutil.make_archive(backup_filename, 'zip', args.directory_name)

    # Reading config information about ftp connection
    host = config[CONFIG_FTP_SECTION][OPTION_HOST]
    port = config[CONFIG_FTP_SECTION][OPTION_PORT]
    username = config[CONFIG_FTP_SECTION][OPTION_USERNAME]
    password = config[CONFIG_FTP_SECTION][OPTION_PASSWORD]

    try:
        ## FTP Connection and upload ##
        # Connect to ftp server and upload backup file
        print("Connecting to FTP server . . .")
        ftp = FTP(host, username, password)
        print('Login ok')
        print('Uploading file . . .')
        ftp.storbinary('STOR ' + backup_filename + '.zip', open(backup_filename + '.zip', 'rb'))
        ftp.quit()
        print('Bye')

        # TODO Remove old backup if it has been there during more than the specified amount of days in config file

        ## Email notification ##

        # User input email address as an argument
        email_subject = None
        email_from = None
        email_to = None
        email_body = None
        if args.email:
            email_subject = "subject"
            email_from = "from"
            email_to = args.email
            email_body = "message body"
        # User has set up the config file
        elif config.has_section(CONFIG_EMAIL_SECTION):
            email_subject = config[CONFIG_EMAIL_SECTION][OPTION_SUBJECT]
            email_from = config[CONFIG_EMAIL_SECTION][OPTION_FROM]
            email_to = config[CONFIG_EMAIL_SECTION][OPTION_TO]
            email_body = config[CONFIG_EMAIL_SECTION][OPTION_BODY]
        else:
            # No email notification
            print("No email provided to notify operations")
            exit()

        message = MIMEText(email_body)
        message['Subject'] = email_subject
        message['From'] = email_from
        message['To'] = email_to

        print("Sending email notification . . .")
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(email_from, [email_to], message.as_string())
        print("Email sent successfully")
        smtp.quit()
    except MessageError:
        print("Error while sending notification error")
