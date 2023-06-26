import xml.etree.ElementTree as ET
import base64
import os
import datetime
import argparse

from mime_types import MIME_TO_EXTENSION


def save_base64_file(encoded_data, output_directory, file_name):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        file_data = base64.b64decode(encoded_data)
    except base64.binascii.Error as e:
        print(f'Error decoding Base64 data: {str(e)}')
        return

    output_filename = os.path.join(output_directory, file_name)
    with open(output_filename, 'wb') as file:
        file.write(file_data)
    print(f'File saved as {output_filename}')


def format_date(milliseconds):
    try:
        timestamp_in_seconds = int(milliseconds) / 1000
    except ValueError as e:
        print(f'Error converting date to integer: {str(e)}')
        return None

    datetime_obj = datetime.datetime.fromtimestamp(timestamp_in_seconds)
    formatted_date = datetime_obj.strftime('%Y%m%d')
    return formatted_date


def extract_files_from_xml(xml_file, base_directory='extracted_files'):
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    try:
        context = ET.iterparse(xml_file, events=('start',))
    except FileNotFoundError as e:
        print(f'Error opening XML file: {str(e)}')
        return

    file_count = 0

    for event, elem in context:
        if elem.tag == 'mms':
            mms_id = elem.attrib.get('_id')
            mms_contact_name = elem.attrib.get('contact_name', 'unknown')
            mms_date_in_ms = elem.attrib.get('date')

        if elem.tag == 'part':
            output_directory = os.path.join(base_directory, mms_contact_name)
            encoded_data = elem.attrib.get('data')
            content_type = elem.attrib.get('ct')

            if encoded_data and ('image' in content_type or 'video' in content_type):
                formatted_date = format_date(mms_date_in_ms)
                if formatted_date is None:
                    continue

                file_extension = MIME_TO_EXTENSION.get(content_type, '.bin')
                save_base64_file(encoded_data, output_directory, f'MMS_{formatted_date}_{mms_id}{file_extension}')
                file_count += 1

        elem.clear()

    print(f'Extracted {file_count} files')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract images and videos from MMS XML backup.')
    parser.add_argument('xml_file', help='Path to the XML file.')
    parser.add_argument('-o', '--output', default='extracted_files', help='Path to the output directory.')
    args = parser.parse_args()

    extract_files_from_xml(args.xml_file, args.output)
