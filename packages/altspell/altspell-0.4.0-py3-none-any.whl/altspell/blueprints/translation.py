'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2024-2025  Nicholas Johnson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import uuid
from flask import Blueprint, request
from flask_caching import Cache
import pytz
from dependency_injector.wiring import inject, Provide
from ..utils.hcaptcha import require_hcaptcha
from ..containers import Container
from ..services import TranslationService
from ..exceptions import (
    MissingKeyError,
    InvalidTypeError,
    EmptyTranslationError,
    SpellingSystemUnavailableError,
    SpellingSystemNotFoundError,
    TranslationNotFoundError
)


bp = Blueprint("translations", __name__, url_prefix='/api/v1')

@bp.route('/translations', methods=['POST'])
@require_hcaptcha
@inject
def translate(translation_service: TranslationService = Provide[Container.translation_service]):
    """
    Endpoint to translate traditional English spelling to alternative English spelling and vice
    versa.

    This endpoint accepts a POST request with a JSON request body and returns the translated
    English text in the JSON Response. Optionally, it saves the resulting translation in the
    database.

    JSON Request Parameters:
    - spellingSystem (str): Name of spelling system used for the translation.
    - forward (bool): Indicates the direction of translation.
    - text (str): Text to be translated.
    - save (bool): Indicates whether save the resulting translation.

    JSON Response Parameters:
    - id (uuid): ID of the translation. (only if 'save' was True in the request)
    - creation_date (DateTime): Date and time translation was inserted into the database. (only if
                                'save' was True in the request)
    - spellingSystem.name (str): Name of spelling system used for the translation.
    - spellingSystem.version (str): Version of spelling system used for the translation.
    - forward (bool): Indicates the direction of translation.
    - traditional_text (str): Text in traditional English spelling.
    - respelled_text (str): Text in alternative English spelling.

    Returns:
        Response: A JSON Response object containing the translated English text.

    Example:

        Request:
        POST /api/v1/translations
        Request Body: {
            "spellingSystem": "lytspel",
            "forward": True,
            "text": "Hello world!",
            "save": True
        }

        Response:
        POST /api/v1/translations
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creation_date": "2020-10-21T05:39:20+00:00",
            "spellingSystem": {
                "name": "lytspel",
                "version": "0.1.0"
            }
            "forward": True,
            "traditional_text": "Hello world!",
            "respelled_text": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Translated English text is returned.
    - 400 Bad Request: JSON request is malformed or requested spelling system is unavailable.
    """
    data = request.json

    save = data.get('save')
    spelling_system = data.get('spellingSystem')
    forward = data.get('forward')
    text = data.get('text')

    try:
        translation = translation_service.translate(
            spelling_system,
            forward,
            text,
            save
        )
    except (
        MissingKeyError,
        InvalidTypeError,
        EmptyTranslationError,
        NotImplementedError,
        SpellingSystemUnavailableError,
        SpellingSystemNotFoundError
    ) as e:
        return {'error': str(e)}, 400

    resp = {
        'spellingSystem': {
            'name': translation.spelling_system.name,
            'version': translation.spelling_system.version
        },
        'forward': translation.forward,
        'traditionalText': translation.traditional_text,
        'respelledText': translation.respelled_text
    }

    if save:
        resp['id'] = translation.id
        resp['creationDate'] = pytz.utc.localize(translation.creation_date).isoformat()

    return resp

@bp.route('/translations/<uuid:translation_id>', methods=['GET'])
@inject
def get_translation(
    translation_id: uuid,
    translation_service: TranslationService = Provide[Container.translation_service],
    cache: Cache = Provide[Container.cache]
):
    """
    Endpoint to get saved translation.

    This endpoint accepts a GET request with the appended translation ID (uuid).

    JSON Response Parameters:
    - id (uuid): ID of the translation.
    - creationDate (DateTime): Date and time translation was inserted into the database.
    - spellingSystem.name (str): Name of spelling system used for the translation.
    - spellingSystem.version (str): Version of spelling system used for the translation.
    - forward (bool): If true, traditional_text -> respelled_text. If false, respelledText -> \
        traditionalText.
    - traditionalText (str): Text in traditional English spelling (necessary if forward is True).
    - respelledText (str): Text in alternative English spelling (necessary if is_forward is False).

    Returns:
        Response: A JSON Response object containing the translated English text.

    Example:

        Request:
        GET /api/v1/translations/7d9be066-6a0b-4459-9242-86dce2df6775

        Response:
        GET /api/v1/translations
        Response Body: {
            "id": "7d9be066-6a0b-4459-9242-86dce2df6775",
            "creationDate": "2020-10-21T05:39:20-0700",
            "spellingSystem": {
                "name": "lytspel",
                "version": "0.2.0"
            }
            "forward": True,
            "traditionalText": "Hello world!",
            "respelledText": "Heló wurld!"
        }

    HTTP Status Codes:
    - 200 OK: Translated English text is returned.
    - 400 Bad Request: Translation ID is not a UUID.
    - 404 Not Found: Translation not found.
    """

    translation = cache.get(translation_id)

    if translation is None:
        try:
            translation = translation_service.get_translation_by_id(translation_id)
        except TranslationNotFoundError as e:
            return {'error': str(e)}, 404

        cache.set(translation_id, translation)

    resp = {
        'id': translation.id,
        'creationDate': pytz.utc.localize(translation.creation_date).isoformat(),
        'spellingSystem': {
            'name': translation.spelling_system.name,
            'version': translation.spelling_system.version
        },
        'forward': translation.forward,
        'traditionalText': translation.traditional_text,
        'respelledText': translation.respelled_text
    }

    return resp
