'''
    Altspell  Flask web app for translating traditional English to respelled
    English and vice versa
    Copyright (C) 2024  Nicholas Johnson

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
import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, Integer, String, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles


class Base(DeclarativeBase):  # pylint: disable=missing-class-docstring,too-few-public-methods
    pass

class UTCnow(expression.FunctionElement):
    """A construct representing the current UTC timestamp."""
    type = DateTime()
    inherit_cache = True

@compiles(UTCnow, "postgresql")
def pg_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the PostgreSQL-specific SQL syntax for retrieving the
    UTC timestamp."""
    return "date_trunc('second', TIMEZONE('utc', CURRENT_TIMESTAMP))"

@compiles(UTCnow, "mssql")
def ms_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the Microsoft SQL-specific SQL syntax for retrieving the
    UTC timestamp."""
    return "GETUTCDATE() AS SMALLDATETIME"

@compiles(UTCnow, "sqlite")
def sqlite_utcnow(_element, _compiler, **_kw):
    """Compiles the `UTCnow` expression to the Sqlite-specific SQL syntax for retrieving the UTC
    timestamp."""
    return "(STRFTIME('%Y-%m-%d %H:%M:%S', 'NOW'))"

class SpellingSystem(Base):  # pylint: disable=too-few-public-methods
    """A table containing the enabled alternate spellings of English."""
    __tablename__ = "spelling_system"
    __table_args__ = (
        UniqueConstraint('name', 'version'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        doc='Sequence number representing alternative spelling of English.'
    )
    name: Mapped[str] = mapped_column(
        String,
        doc='Name of alternative spelling of English.'
    )
    version: Mapped[str] = mapped_column(
        String,
        doc='Version number of alternative spelling of English'
    )
    pretty_name: Mapped[str] = mapped_column(
        String,
        doc='Pretty name of alternative spelling of English.'
    )
    facts: Mapped[Optional[JSON]] = mapped_column(
        JSON,
        doc='Optional JSON document with miscellaneous info about alternative spelling of English.'
    )

    translations: Mapped[List["Translation"]] = relationship(
        back_populates="spelling_system",
        doc='All translations that use the alternative spelling of English.'
    )

class Translation(Base):  # pylint: disable=too-few-public-methods
    """A table containing the saved translations."""
    __tablename__ = "translation"

    id: Mapped[uuid] = mapped_column(
        Uuid,
        primary_key=True,
        doc='Sequence number representing translation.'
    )
    creation_date: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        server_default=UTCnow(),
        doc='DateTime representing when the translation was inserted into the database.'
    )
    forward: Mapped[bool] = mapped_column(
        Boolean,
        doc='Boolean representing which direction the translation occurred in. I.e: Either ' \
            'traditional English spelling => alternative English spelling or alternative ' \
            'English spelling => traditional English spelling.'
    )
    traditional_text: Mapped[str] = mapped_column(
        String,
        doc='Text in traditional English spelling.'
    )
    respelled_text: Mapped[str] = mapped_column(
        String,
        doc='Text in alternative English spelling.'
    )
    spelling_system_id: Mapped[int] = mapped_column(
        ForeignKey('spelling_system.id'),
        doc='Sequence number representing alternative spelling of English.'
    )

    spelling_system: Mapped["SpellingSystem"] = relationship(
        back_populates="translations",
        doc='The alternative spelling of English that was used by the translation.'
    )
