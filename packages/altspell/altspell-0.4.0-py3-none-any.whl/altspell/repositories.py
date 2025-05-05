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

import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from .model import SpellingSystem, Translation
from .exceptions import TranslationNotFoundError, SpellingSystemNotFoundError


class TranslationRepository:
    """Repository for database operations related to translations."""
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def add(
        self,
        forward: bool,
        traditional_text: str,
        respelled_text: str,
        spelling_system_id: int
    ) -> Translation:
        """
        Add a translation to the database.

        Args:
            forward (bool): True if translated to the alternative spelling system. False if \
                translated to traditional English spelling.
            traditional_text (str): Text in traditional English spelling.
            respelled_text (str): Text in the alternative English spelling system.
            spelling_system_id (int): Id of the alternative spelling system.

        Returns:
            Translation: The translation object added to the database.
        """
        translation = Translation(
            id=uuid.uuid4(),
            forward=forward,
            traditional_text=traditional_text,
            respelled_text=respelled_text,
            spelling_system_id=spelling_system_id
        )
        self.db.session.add(translation)
        try:
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
        translation = (
            self.db.session.query(Translation)
            .options(selectinload(Translation.spelling_system))
            .filter(Translation.id == translation.id)
            .first()
        )
        return translation

    def get_by_id(self, translation_id: uuid) -> Translation:
        """
        Retrieve a translation by id.

        Args:
            translation_id (uuid): Id of the requested translation.

        Returns:
            Translation: The translation object corresponding to translation_id.
        """
        translation = (
            self.db.session.query(Translation)
            .options(selectinload(Translation.spelling_system))
            .filter(Translation.id == translation_id)
            .first()
        )
        if not translation:
            raise TranslationNotFoundError(translation_id)
        return translation

class SpellingSystemRepository:
    """Repository for database operations related to alternative spelling systems."""
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def add(self, name: str, version: str, pretty_name: str, facts: str | None) -> SpellingSystem:
        """
        Add an alternative spelling system.

        Args:
            name (str): Name of the alternative spelling system.
            version (str): Version of the alternative spelling system.
            pretty_name (str): Pretty name of the alternative spelling system.
            facts (str): JSON string for miscellaneous structured info about the spelling system
                plugin.

        Returns:
            SpellingSystem: The alternative spelling system object added to the database.
        """

        spelling_system = SpellingSystem(
            name=name,
            version=version,
            pretty_name=pretty_name,
            facts=facts
        )
        self.db.session.add(spelling_system)
        try:
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
        spelling_system = (
            self.db.session.query(SpellingSystem)
            .filter(SpellingSystem.name == name, SpellingSystem.version == version)
            .first()
        )
        return spelling_system

    def get_all(self):
        """Retrieve a list of enabled alternative spelling systems."""
        return self.db.session.query(SpellingSystem).all()

    def get(self, name: str, version: str) -> SpellingSystem:
        """
        Retrieve an alternative spelling system object by alternative spelling system name and
        version.

        Args:
            name (str): Name of the alternative spelling system.
            version (str): Version of the alternative spelling system.

        Returns:
            SpellingSystem: The alternative spelling system object corresponding to \
                name and version.
        """
        spelling_system = (
            self.db.session.query(SpellingSystem)
            .filter(SpellingSystem.name == name, SpellingSystem.version == version)
            .first()
        )
        if not spelling_system:
            raise SpellingSystemNotFoundError(f"{name} v{version}")
        return spelling_system
