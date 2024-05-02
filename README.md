# OneDrive Downloader
OneDrive-Downloader is created to simplify downloading files from OneDrive using Microsoft Graph API

# Requirements
In order to use the tool, it's required to install python packages from requirements.txt

`python -m pip install -r requirements.txt`

# How to use
Use command line arguments, environment variables and JSON-file to let the downloader know what credentials to use and what files to download.
Refer to `items_template.json` to learn how to pass list of files to be downloaded.

The following command line arguments required:
- `-c` or `--client` to specify client_id of the application which is registred in Microsoft Azure
- `-s` or `--secret` to specify secret sequence for the application
- `-t` or `--tenant` to specify tenant_id of the application
The following optional command line agruments can be passed:
- `-i` or `--items` to specify a path to JSON-file which is used to list files to be downloaded. Default is `items_template.json`
- `-o` or `--output` to specify a path where the files should be downloaded. Default is `.`

Upon first use it's required to sign in using user's credentials to be able to claim tokens. The tool puts tokens into environmental variables
`ONEDRIVE_ACCESS_TOKEN` and `ONEDRIVE_REFRESH_TOKEN`. Further, these variables are used in downloading files from OneDrive.

# Example

`python app/main.py -c aaaaaaaa-bbbb-cccc-dddd-eeeeeeffffff -s bS78Q~-xbqysS3gOgJaNh~jcrRNrBiy0-25P5cqC -t bbbbbbbb-aaaa-cccc-dddd-eeeeeeffffff -i items.json -o output`