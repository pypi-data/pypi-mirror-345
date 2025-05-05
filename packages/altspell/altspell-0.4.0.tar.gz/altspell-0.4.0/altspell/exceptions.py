'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2025  Nicholas Johnson

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

from typing import Type


class NotFoundError(Exception):
    """Exception for database records that cannot be found."""
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")

class TranslationNotFoundError(NotFoundError):
    """Exception for Translations that cannot be found."""
    entity_name: str = "Translation"

class SpellingSystemNotFoundError(NotFoundError):
    """Exception for spelling systems that cannot be found."""
    entity_name: str = "Spelling system"

class MissingKeyError(Exception):
    """Exception for missing required JSON request body keys."""
    def __init__(self, key_name: str):
        super().__init__(f"Missing key: {key_name}")

class InvalidTypeError(Exception):
    """Exception for JSON request body keys with incorrect types."""
    def __init__(self, key_name: str, cls: Type):
        super().__init__(f"Key '{key_name}' must be of type '{cls.__name__}'")

class EmptyTranslationError(Exception):
    """Exception for empty translation text."""
    def __init__(self):
        super().__init__("Cannot save an empty translation")

class FwdTranslationNotImplementedError(NotImplementedError):
    """Exception for attempted unimplemented forward translations."""
    def __init__(self):
        super().__init__("Forward translation is not implemented for this spelling system")

class BwdTranslationNotImplementedError(NotImplementedError):
    """Exception for attempted unimplemented backward translations."""
    def __init__(self):
        super().__init__("Backward translation is not implemented for this spelling system")

class SpellingSystemUnavailableError(Exception):
    """Exception for attempted translations with unavailable spelling systems."""
    def __init__(self, spelling_system: str):
        super().__init__(f"Spelling system '{spelling_system}' is unavailable")
