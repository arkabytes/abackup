#!/usr/bin/python3

"""abbackup
 Create and upload backups to a FTP Server. It also sends an email when task is done
 Author            Santiago Faci <santi@arkabytes.com>
 Version           0.2
 Date              2018-02-16
 Python version    3.5
"""

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
from datetime import date, datetime


VERSION = '0.2'
CWD = os.getcwd()
TMP_PATH = '/tmp/'
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(CURRENT_DIRECTORY, 'abbackup.log')

CONFIG_FILE = os.path.join(CURRENT_DIRECTORY, 'abbackup.conf')
CONFIG_FTP_SECTION = 'ftp_server'
CONFIG_EMAIL_SECTION = 'email_settings'
CONFIG_BACKUP_SECTION = 'backup'
CONFIG_DB_SECTION = 'db'

BACKUP_NAME = 'name'
ROTATION = 'rotation'
HOST = 'host'
PORT = 'port'
USERNAME = 'username'
PASSWORD = 'password'
SUBJECT = 'subject'
FROM = 'from'
TO = 'to'
MESSAGE = 'message'
BACKEND = 'backend'

#LOG_FORMAT = '%(asctime)-15s:%(levelname)s:%(message)s'
LOG_FORMAT = '%(levelname)s:%(message)s'
DEBUG = False


def check_config_file():
    """Read and check if config file is formerly created"""
    global config
    config = configparser.ConfigParser()
    config.sections()
    config.read(CONFIG_FILE)

    # Check if config file has the proper section
    if not config.has_section(CONFIG_FTP_SECTION):
        logging.error("Invalid config file (no '" + CONFIG_FTP_SECTION + "' section)")
        exit()

    # Check if config file provided all the needed information to connect to the FTP server
    if not config.has_option(CONFIG_FTP_SECTION, HOST) or \
            not config.has_option(CONFIG_FTP_SECTION, PORT) or \
            not config.has_option(CONFIG_FTP_SECTION, USERNAME) or \
            not config.has_option(CONFIG_FTP_SECTION, PASSWORD):
        logging.error('Invalid config file (check syntax)')
        exit()


def get_server_configuration():
    """Get server configuration parameters from config file"""
    global server_config
    server_config = dict()
    # Reading config information about FTP connection
    # TODO In the future, if abbackup support new protocols, we will have to include OPTION_PROTOCOL as a new option
    server_config[HOST] = config[CONFIG_FTP_SECTION][HOST]
    server_config[PORT] = config[CONFIG_FTP_SECTION][PORT]
    server_config[USERNAME] = config[CONFIG_FTP_SECTION][USERNAME]
    server_config[PASSWORD] = config[CONFIG_FTP_SECTION][PASSWORD]

    return server_config


def get_email_configuration():
    """Get email configuration parameters from config file"""
    global email_config
    email_config = dict()
    # Reading config information about email notification
    email_config[MESSAGE] = config[CONFIG_EMAIL_SECTION][MESSAGE]
    email_config[SUBJECT] = config[CONFIG_EMAIL_SECTION][SUBJECT]
    email_config[FROM] = config[CONFIG_EMAIL_SECTION][FROM]
    email_config[TO] = config[CONFIG_EMAIL_SECTION][TO]

    return email_config


def get_db_configuration():
    """Get database configuration parameters from config file"""
    global db_config
    db_config = dict()
    # Reading config information about databases
    db_config[BACKEND] = config[CONFIG_DB_SECTION][BACKEND]
    db_config[HOST] = config[CONFIG_DB_SECTION][HOST]
    db_config[PORT] = config[CONFIG_DB_SECTION][PORT]
    db_config[USERNAME] = config[CONFIG_DB_SECTION][USERNAME]
    db_config[PASSWORD] = config[CONFIG_DB_SECTION][PASSWORD]

    return email_config


def send_email(message=None):
    """Send a notification email to notify something"""
    if message:
        email = MIMEText(message)
    else:
        email = MIMEText(email_config[MESSAGE])
    email['Subject'] = email_config[SUBJECT]
    email['From'] = email_config[FROM]
    email['To'] = email_config[TO]

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(email_config[FROM], [email_config[TO]], email.as_string())
    smtp.quit()


def configure_logging(verbose):
    """Set logging configuration to log into a file and to stdout"""
    if verbose:
        level = logging.INFO
    else:
        level = logging.ERROR

    logging.basicConfig(format=LOG_FORMAT, level=level,
                        handlers=[
                            logging.FileHandler(LOG_FILE),
                            logging.StreamHandler()
                        ])


def get_backups_list(connection, name, extension):
    """Get a list containing all the filenames for an specified backup name"""
    return connection.nlst(name + '*.' + extension)


def rotate_backup(connection, name, extension):
    """Rotate an specified backup (zip or sql)"""
    backups = get_backups_list(connection, name, extension)
    if len(backups) > rotation_count:
        # Remove oldest backup from server
        logging.info('deleting oldest backup in the server (' + backups[0].split('_')[1].split('.')[0] + ')')
        ftp.delete(backups[0])


def get_backup_date(filename):
    """Get the date for an specified backup filename"""
    backup_date = filename.split('_')[1].split('.')[0]
    return backup_date


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', help='Backup name', metavar='NAME')
backup = parser.add_mutually_exclusive_group(required=True)
backup.add_argument('-d', '--directory-name', help='Create backup from the specified directory', metavar='DIRECTORY_NAME')
backup.add_argument('-b', '--databases', help='Backup databases using configuration file', action='store_true')
parser.add_argument('-e', '--email', help='Overrides the default email address from config file (for notification purpose)', metavar='EMAIL_ADDRESS')
parser.add_argument('-l', '--list-backups', help='List backups (from config name or an specified one passing the --name argument)', action="store_true")
parser.add_argument('-v', '--verbose', help='Print debug information', action='store_true')

print('\nabbackup ' + VERSION + ': A backup tool (http://www.github.com/arkabytes/abbackup)')
args = parser.parse_args()

# Set DEBUG mode (or not)
if args.verbose:
    DEBUG = True

# Initialize logging system
configure_logging(DEBUG)

# Global variable to store config file information
config = None

# Check if user has provided at least 1 argument (directory to make backup)
if len(sys.argv) == 1:
    logging.error("no arguments provided. Execute '" + sys.argv[0] + " -h' for help")
    exit()

# Check if config file exists
if not os.path.isfile(CONFIG_FILE):
    logging.error('no config file. You must to create it to provide FTP server configuration')
    exit()

# Check and read configuration file
check_config_file()

# Get backup name from argument or config file
backup_name = ''
if args.name:
    backup_name = args.name
else:
    backup_name = config[CONFIG_BACKUP_SECTION][BACKUP_NAME]
rotation_count = int(config[CONFIG_BACKUP_SECTION][ROTATION])

"""
LIST BACKUPS
"""
if args.list_backups:
    # Reading config information about ftp connection
    server_config = get_server_configuration()

    logging.info('connecting to FTP server')
    ftp = None
    try:
        ftp = FTP(server_config[HOST], server_config[USERNAME], server_config[PASSWORD], timeout=5)
        results = []
        results = ftp.nlst(backup_name + '*')
        if len(results) > 0:
            backup_date = get_backup_date(results[len(results) - 1])
        else:
            backup_date = 'none'
        print('listing backups (' + backup_name + ', rotation = ' + str(rotation_count) + ', last_backup = ' + backup_date + ')')
        if len(results) > 0:
            for result in results:
                try:
                    # size command is not standarized (no every ftp server supports it)
                    print(' - ' + result + ' ' + str(round(ftp.size(result) / (1024 * 1024), 3)) + ' MB')
                except:
                    print(' - ' + result + ' ? MB')
        else:
            print('no backups for given name')
    except OSError as ose:
        logging.error('error trying to connect to FTP server. (' + ose.__str__() + ')')
        exit()
    except Exception as e:
        logging.error('an exception has occurred. (' + e.__str__() + ')')
        exit()
    logging.info('backups listed successfully. Connection terminated')
    ftp.quit()
    exit()

# User has to select directory_name, databases or both
if not args.directory_name or not args.databases:
    logging.error('no operation selected. Nothing to do')
    exit()

# backup_filename: backup_name + datetime
backup_filename = backup_name + '_' + str(datetime.today().strftime('%Y-%m-%d_%H:%M:%S'))

"""
MAKE BACKUP / DATABASES
"""
# Reading config information about ftp connection
server_config = get_server_configuration()
# Reading config information about databases (if proceed)
if args.databases:
    db_config = get_db_configuration()

# Read email config data (email address can have been introduced manually)
email_config = None
if config.has_section(CONFIG_EMAIL_SECTION):
    email_config = get_email_configuration()
    if args.email:
        email_config[TO] = args.email
else:
    # No email notification
    logging.error('no email provided to notify operations')
    exit()
try:
    logging.info('starting new backup %s/%s', backup_name, backup_filename)
    ''' Making backup '''
    if args.directory_name:
        # Create zip file from directory
        shutil.make_archive(TMP_PATH + backup_filename, 'zip', args.directory_name)
        zip_filename = backup_filename
        logging.info('data backup file created')
    if args.databases:
        # Create backup from databases
        if db_config[BACKEND] == 'mysql':
            db_backup_command = 'mysqldump -h ' + db_config[HOST] + ' --port ' + db_config[PORT] + ' -u ' + db_config[
                USERNAME] + ' -p' + \
                                db_config[PASSWORD] + ' --all-databases > ' + TMP_PATH + backup_filename + '.sql'
            os.system(db_backup_command)
            logging.info('sql backup file created')
        elif db_config[BACKEND] == 'postgresql':
            pass

    ''' FTP Connection and upload '''
    # Connect to ftp server and upload backup file
    logging.info('connecting to FTP server . . .')
    ftp = FTP(server_config[HOST], server_config[USERNAME], server_config[PASSWORD], timeout=5)
    logging.info('login ok')
    logging.info('uploading file/s . . .')
    if args.directory_name:
        ftp.storbinary('STOR ' + backup_filename + '.zip', open(TMP_PATH + zip_filename + '.zip', 'rb'))
    if args.databases:
        ftp.storbinary('STOR ' + backup_filename + '.sql', open(TMP_PATH + backup_filename + '.sql', 'rb'))
    logging.info('file/s uploaded successfully')

    # Make backup rotation based on configuration file ('rotation' option)
    logging.info('checking rotation backup . . .')
    if rotation_count != 0:
        if args.directory_name:
            rotate_backup(ftp, backup_name, 'zip')
        if args.databases:
            rotate_backup(ftp, backup_name, 'sql')

    ftp.quit()

    # TODO Then, abbackup should be able to notify if both (or not) are finished successfully
    ''' Email notification '''
    try:
        logging.info('sending email notification . . .')
        send_email()
        logging.info('email sent successfully')
        logging.info('finished backup %s/%s', backup_name, backup_filename)
    except MessageError:
        logging.error('error while sending notification error')
    except ConnectionRefusedError:
        logging.error('error while connection with the smtp server:connection refused!')

    os.remove(TMP_PATH + backup_filename + '.zip')
    logging.info('removed local file (' + backup_filename + '.zip' + ')')
except ftplib.Error as e:
    logging.error('error while uploading file')
    send_email('error while uploading file')
except socket.timeout:
    logging.error('ftp connection timeout excedeed')
    send_email('ftp connection timeout excedeed')
except Exception as e:
    logging.error('error while creating backup: ' + e)
    send_email('error while creating backup')
