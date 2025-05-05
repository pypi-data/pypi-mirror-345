'''
    Altspell-Lytspel  Lytspel plugin for altspell.
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

import threading
from lytspel.conv import Converter as FwdTranslator
from altspell_plugins import PluginBase
from .reverse import Translator as RevTranslator


class Plugin(PluginBase):
    def __init__(self):
        self._name = "lytspel"
        self._pretty_name = "Lytspel"

        self._lock = threading.Lock()
        self._fwd_translator = FwdTranslator()
        self._rev_translator = RevTranslator()

    @property
    def name(self) -> str:
        return self._name

    @property
    def pretty_name(self) -> str:
        return self._pretty_name

    def translate_to_respelling(self, traditional_text: str) -> str:
        # use a lock to make the function thread-safe
        with self._lock:
            para = self._fwd_translator.convert_para(traditional_text)

        return para

    def translate_to_traditional_spelling(self, respelled_text: str) -> str:
        return self._rev_translator.translate_para(respelled_text)
