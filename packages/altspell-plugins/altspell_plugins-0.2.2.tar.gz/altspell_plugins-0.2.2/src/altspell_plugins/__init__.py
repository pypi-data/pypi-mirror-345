'''
    Altspell-Plugins  Plugin interface for Altspell
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

from abc import ABC, abstractmethod


class PluginBase(ABC):
    """
    An interface for spelling system plugins. Concrete subclasses must be named 'Plugin'.

    Methods:
        translate_to_respelling(traditional_text: str) -> str:
            Thread-safe method for translating from traditional English spelling to alternative
            English spelling.
        translate_to_traditional_spelling(respelled_text: str) -> str:
            Thread-safe method for translating from alternative English spelling to traditional
            English spelling.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Identifier for the spelling system plugin. Used in Altspell API calls.
        """

    @property
    @abstractmethod
    def pretty_name(self) -> str:
        """
        Human-readable name for the spelling system plugin. Intended for frontend use.
        """

    @property
    def facts(self) -> str | None:
        """
        JSON string for miscellaneous structured info about the spelling system plugin. Can be
        overridden in concrete subclass to provide metadata about spelling system plugin.

        E.g:
            .. code-block:: json
            {
                "author": "Christian Siefkes",
                "description": "A Simple Phonetic Respelling for the English Language",
                "reference": "https://www.lytspel.org/rules"
            }
        """
        return None

    @abstractmethod
    def translate_to_respelling(self, traditional_text: str) -> str:
        """
        Thread-safe method for translating from traditional English spelling to alternative
        English spelling. All concrete subclasses must implement or raise a NotImplementedError.

        Args:
            traditional_text (str): Text written in the traditional English spelling.

        Returns:
            str: Text written in the alternative English spelling.
        """

    @abstractmethod
    def translate_to_traditional_spelling(self, respelled_text: str) -> str:
        """
        Thread-safe method for translating from alternative English spelling to traditional
        English spelling. All concrete subclasses must implement or raise a NotImplementedError.

        Args:
            respelled_text (str): Text written in the alternative English spelling.

        Returns:
            str: Text written in the traditional English spelling.
        """
