# abbackup

Python script to create backups

# About

**abbackup** is a Python script created to make and upload backups to a FTP server. It also notifies, sending an e-mail, when job is done.
The main idea is to run it as a cron job to automate backup creation in a server or wherever you have important data you want to backup.

# Features

  * Create backup from a folder
  * Create MySQL databases backup
  * Upload automatically the backup to a FTP server
  * Notify sending an e-email when job is done
  * Register activity in a log file
  * List backups (from FTP server)
  * Notify sending an e-mail also when something was wrong
  * Basic backup rotation in the FTP server based on the number of files you want to keep

##### TODO
  
  * Support for other protocols like SCP
  * Support for PostgreSQL databases backup
  * Any suggestions? [just ask](https://github.com/arkabytes/abbackup/issues)

# Requirements

  * Python >= 3
  

#### Notice

**abbackup** is developed under Linux and it has not been tested under any other Operating System. Anyway, it should run without problems under any Unix-friendly OS.

# Installation

abbackup doest no require any installation process. It is only a Python script that you can run directly.
The only thing you need is to customize the configuration file `abbackup.conf`. You can find a template below.

Some sections are mandatory and others are only necessary if you need them:
  * _[backup]_ is mandatory
  * _[db]_ is only necessary if you want to create databases backup
  * _[ftp_server]_ is mandatory
  * _[email_settings]_ is only necessary if you want to receive email notifications
  
```ini
[backup]
name = my_backup_name
rotation = 2                # 0 means 'no rotation'
 
[db]
backend = mysql
host = localhost
port = mysql_port
username = your_db_username
password = your_db_password
 
[ftp_server]
host = 192.168.1.7
port = 21
username = your_ftp_user
password = your_ftp_password
 
[email_settings]
subject = Backup done
from = non-reply@yourdomain.com
to = user@yourdomain.com
message = Backup done successfully
```

You can download a packaged release in the [releases section](https://github.com/arkabytes/abbackup/releases)

> Notice that abbackup generate a log file with some debug information in the same directory where you run the script.

# Usage

```bash
abbackup 0.2.2: A backup tool (http://www.github.com/arkabytes/abbackup)
usage: abbackup.py [-h] [-n NAME] (-d DIRECTORY_NAME | -b | -l)
                   [-e EMAIL_ADDRESS] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Backup name
  -d DIRECTORY_NAME, --directory-name DIRECTORY_NAME
                        Create backup from the specified directory
  -b, --databases       Backup databases using configuration file
  -l, --list-backups    List backups (from config name or an specified one
                        passing the --name argument)
  -e EMAIL_ADDRESS, --email EMAIL_ADDRESS
                        Overrides the default email address from config file
                        (for notification purpose)
  -v, --verbose         Print debug information
```

For example:

```bash
santi@zenbook:$ ./abbackup.py --directory-name path/to/a/directory -v
``` 

You can run it as a cron job writting next line in your crontab if you want, for example, create a backup once a day at midnight:

```bash
0 0 * * * /path/to/abbackup.py --directory-name path/to/a/directory -v
```

# Documentation

By the moment there is no documentation about **abbackup**.

# Author

Santiago Faci <santi@codeandcoke.com>
