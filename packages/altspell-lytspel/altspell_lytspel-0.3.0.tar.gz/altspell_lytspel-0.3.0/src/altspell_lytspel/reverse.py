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

import csv
import importlib.resources as pkg_resources
from lytspel.util import get_elem
from nlp_provider import shared_nlp


class Dictionary:
    def __init__(self):
        self.dict = {}
        self._populate_dict()

    def _populate_dict(self):
        with pkg_resources.open_text('lytspel', 'lytspel-dict.csv') as csvfile:
            csvreader = csv.reader(csvfile)

            # skip header
            next(csvreader)

            for row in csvreader:

                # Discard redirects so that Lytspel words map to only one English word
                #
                # Redirects are typically valid alternate spellings of a word.
                # E.g: British English spelling vs American English spelling
                if get_elem(row, 2):
                    continue

                # Don't capture the part of speech (PoS)
                # PoS is used for the forward translation, not the backward translation
                tradspell = get_elem(row, 0)
                lytspel = get_elem(row, 3)

                self.dict[lytspel] = tradspell

class Translator:
    _dict = Dictionary()
    _nlp = shared_nlp

    def translate_para(self, text: str) -> str:
        out_tokens = []

        doc = Translator._nlp(text)
        for token in doc:
            token_lower = token.text.lower()

            if token_lower in Translator._dict.dict:
                if token.text[0].isupper():
                    word = Translator._dict.dict[token_lower]
                    word = word[0].upper() + word[1:]
                    out_tokens.append(word)
                else:
                    out_tokens.append(Translator._dict.dict[token_lower])
            elif token.text in Translator._dict.dict:
                out_tokens.append(Translator._dict.dict[token.text])
            else:
                out_tokens.append(token.text)

            out_tokens.append(token.whitespace_)

        return ''.join(out_tokens)
