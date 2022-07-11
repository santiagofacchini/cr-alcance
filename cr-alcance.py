import re
import os
import ftplib
import requests


# Download directory
download_directory = '/usr/src/app/downloads/'

# Year to scrape
year = 2022

# FTP connection
ftp_connection = ftplib.FTP(
    os.environ['PRODUCCION_HOST'],
    os.environ['PRODUCCION_USER'],
    os.environ['PRODUCCION_PASS'],
)
print(ftp_connection.getwelcome())
ftp_directory = '/Carga_manual/11475/backup'
ftp_connection.cwd(ftp_directory)
ftp_sub_directories = ftp_connection.nlst()

print('Generating list of files in ftp, this might take a while...')
ftp_alcances = []
for sub_directory in ftp_sub_directories:
    for file in ftp_connection.nlst(f'{ftp_directory}/{sub_directory}'):
        if 'ALCA' in file:
            ftp_alcances.append(file)
ftp_connection.quit()
print(f'Found {len(ftp_alcances)} alcances in ftp.')

# Seed url
seed_url = f'https://www.imprentanacional.go.cr/app_httphandlers/GetAlcancesList.ashx?year={year}'

# Requests session
session = requests.Session()

# API Response
alcances_json = session.get(url=seed_url, verify=False).json()

# Download PDF files
for alcance in alcances_json:
    alcance_link = alcance['Link']
    alcance_name = re.sub(
        r'/pub/\d{4}/\d{2}/\d{2}/(ALCA[\d\w_]+\.pdf)',
        r'\1',
        alcance_link,
    )

    # Delete file from local host if already in vLex
    if os.path.isfile(f'{download_directory}{alcance_name}') and alcance_name in ftp_alcances:
        os.remove(f'{download_directory}{alcance_name}')

    # Download file
    elif not os.path.isfile(f'{download_directory}{alcance_name}'):
        if alcance_name not in ftp_alcances:
            print(f'Downloading {alcance_name}...')
            alcance_response = session.get(f'https://www.imprentanacional.go.cr{alcance_link}', verify=False)
            print(alcance_response.status_code)

            with open(f'{download_directory}{alcance_name}', 'wb') as alcance_pdf:
                alcance_pdf.write(alcance_response.content)

            print('OK!')

# Close requests session
session.close()
