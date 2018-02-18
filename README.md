# abbackup

Python script to create backups

# About

**abbackup** is a Python script created to make and upload backups to a FTP server. It also notifies, sending an e-mail, when job is done.
The main idea is to run it as a cron job to automate backup creation in a server or wherever you have important data you want to backup.

# Features

  * Create backup from a folder
  * Upload automatically the backup to a FTP server
  * Notify sending an e-email when job is done
  * Register activity in a log file
  * List backups (from FTP server)
  * Notify sending an e-mail also when something was wrong
  
##### TODO
  
  * Backup rotation in the FTP server
  * And more . . .

# Requirements

  * Python >= 3
  

#### Notice

**abbackup** is developed under Linux and it has not been tested under any other Operating System. Anyway, it should run without problems under any Unix-friendly OS.

# Installation

abbackup doest no require any installation process. It is only a Python script that you can run directly.
The only thing you need is to customize the configuration file `abbackup.conf`. You can find a template below.

```ini
[backup]
name = my_backup_name

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
abbackup 0.2: A backup tool (http://www.github.com/arkabytes/abbackup)
usage: abbackup.py [-h] [--directory-name DIRECTORY_NAME] [--name NAME]
                   [--email EMAIL_ADDRESS] [--list-backups] [-v]

optional arguments:
  -h, --help            show this help message and exit
  --directory-name DIRECTORY_NAME
                        Directory to back up
  --name NAME           Backup name
  --email EMAIL_ADDRESS
                        Overrides the default email address for notification
                        purpose
  --list-backups        List backups (from config name or an specified one
                        passing the --name argument)
  -v                    Print debug information
```

Currently you can only run the script passing `--directory-name` argument:

```bash
santi@zenbook:$ ./abbackup.py --directory-name path/to/a/dirrectory
``` 

You can run it as a cron job writting next line in your crontab if you want, for example, create a backup once a day at midnight:

```bash
0 0 * * * /path/to/abbackup.py --directory-name path/to/a/directory 
```

# Documentation

By the moment there is no documentation about **abbackup**.

# Author

Santiago Faci <santi@arkabytes.com>
