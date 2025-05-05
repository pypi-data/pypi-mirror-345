'''
    Altspell  Soundspel plugin for altspell.
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
from importlib.resources import files
from nlp_provider import shared_nlp
from . import data


class FwdDictionary:
    def __init__(self):
        self.dict = {}
        self._populate_dict()

    def _populate_dict(self):
        with files(data).joinpath('soundspel-dict.csv').open('r') as file:

            for row in csv.reader(file):
                tradspell = row[0]
                soundspel = row[1]

                self.dict[tradspell] = soundspel

class RevDictionary:
    def __init__(self):
        self.dict = {}
        self._populate_dict()

    def _populate_dict(self):
        with files(data).joinpath('soundspel-dict.csv').open('r') as file:

            for row in csv.reader(file):
                tradspell = row[0]
                soundspel = row[1]

                self.dict[soundspel] = tradspell

class Translator:
    _nlp = shared_nlp

def _process_lowercase_key(token, key, dictionary, out_tokens):
    if token.text[0].isupper():
        word = dictionary.dict[key]
        word = word[0].upper() + word[1:]
        out_tokens.append(word)
    else:
        out_tokens.append(dictionary.dict[key])

class FwdTranslator(Translator):
    _dict = FwdDictionary()

    def translate_para(self, text: str) -> str:
        out_tokens = []

        doc = Translator._nlp(text)
        for token in doc:
            token_lower = token.text.lower()

            if token_lower in self._dict.dict:
                _process_lowercase_key(token, token_lower, self._dict, out_tokens)
            elif token.text in self._dict.dict:
                out_tokens.append(self._dict.dict[token.text])
            else:
                out_tokens.append(token.text)

            out_tokens.append(token.whitespace_)

        return ''.join(out_tokens)

class RevTranslator(Translator):
    _dict = RevDictionary()

    def translate_para(self, text: str) -> str:
        out_tokens = []

        doc = Translator._nlp(text)
        for token in doc:
            token_lower = token.text.lower()

            if token_lower in self._dict.dict:
                _process_lowercase_key(token, token_lower, self._dict, out_tokens)
            elif token.text in self._dict.dict:
                out_tokens.append(self._dict.dict[token.text])
            else:
                out_tokens.append(token.text)

            out_tokens.append(token.whitespace_)

        return ''.join(out_tokens)
