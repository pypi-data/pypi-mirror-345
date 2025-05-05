import requests
from werkzeug.utils import secure_filename

API_URL = 'https://api.platerecognizer.com/v1/plate-reader/'
API_TOKEN = 'd32a25fbee640d8d959e51f0346e289d96ea7586'

def recognize_plate(file):
    """
    This function recognizes the license plate from an image file.

    :param file: The image file containing the license plate.
    :return: A dictionary with the plate information or error message.
    """
    filename = secure_filename(file.filename)

    try:
        response = requests.post(
            API_URL,
            files={'upload': file},
            data={'config': '{"mmc": true, "blur": true}'},
            headers={'Authorization': f'Token {API_TOKEN}'}
        )
        result = response.json()

        if 'results' in result and result['results']:
            item = result['results'][0]  # First result
            plate = item.get('plate', '').upper()
            region = item.get('region', {}).get('code', '')

            return {
                'filename': filename,
                'plate': plate,
                'region_code': region
            }

        else:
            return {
                'filename': filename,
                'error': 'No plate detected or invalid image.'
            }

    except Exception as e:
        return {'filename': filename, 'error': str(e)}
