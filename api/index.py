# api/get_channel_data.py

from flask import jsonify
import requests
import gzip
import xml.etree.ElementTree as ET
import json

def download_and_unzip(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with gzip.open(response.raw, 'rt', encoding='utf-8') as gz_file:
        xml_content = gz_file.read()

        root = ET.fromstring(xml_content)
        programs = []

        for program_elem in root.findall('.//programme'):
            program_data = {
                'start': program_elem.get('start'),
                'stop': program_elem.get('stop'),
                'channel': program_elem.get('channel'),
                'catchup-id': program_elem.get('catchup-id'),
                'title': program_elem.find('title').text,
                'desc': program_elem.find('desc').text,
                'icon': program_elem.find('icon').get('src')
            }

            programs.append(program_data)

        return programs

def handler(request):
    # Extract parameters from the request
    channel_id = request.query.get('id')
    start_prefix = request.query.get('date')

    # URL to your epg.xml.gz file
    epg_url = 'https://raw.githubusercontent.com/mitthu786/tvepg/main/tataplay/epg.xml.gz'

    # Call the function to get program data
    programs = download_and_unzip(epg_url)

    # Filter programs for the specified channel ID and date
    channel_programs = [program for program in programs if program['channel'] == channel_id and program['start'].startswith(start_prefix)]

    # Return JSON response
    return jsonify(channel_programs)
