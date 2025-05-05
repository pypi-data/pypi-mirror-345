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

from dependency_injector import containers, providers
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .services import SpellingSystemService, TranslationService
from .repositories import SpellingSystemRepository, TranslationRepository


class Container(containers.DeclarativeContainer):  # pylint: disable=too-few-public-methods
    """Container for injecting dependencies into blueprint modules."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            ".blueprints.spelling_system", 
            ".blueprints.translation",
            ".utils.populate_spelling_system_table"
        ]
    )

    db = providers.Singleton(SQLAlchemy)

    cache = providers.Singleton(Cache)

    migrate = providers.Singleton(Migrate)

    spelling_system_repository = providers.Singleton(
        SpellingSystemRepository,
        db=db
    )

    spelling_system_service = providers.Factory(
        SpellingSystemService,
        spelling_system_repository=spelling_system_repository
    )

    translation_repository = providers.Singleton(
        TranslationRepository,
        db=db
    )

    translation_service = providers.Factory(
        TranslationService,
        translation_repository=translation_repository,
        spelling_system_repository=spelling_system_repository
    )
