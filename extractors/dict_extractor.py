#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# TODO: Implement it, e.g. getting data from wikidata
from extractors.base_extractor import BaseExtractor

person_suffixes = [
    "menyatakan",
    "menegaskan",
    "menjelaskan",
    "mengungkapkan",
    "mengatakan",
    "menambahkan",
    "bilang",
    "S.Kom",
    "M.Kom",
    "S.H.",
]


class DictExtractor(BaseExtractor):
    """
    Extracts entities from text using a dictionary of entities and their synonyms
    using dictionary-trie data structure
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dictionary = kwargs.get("dictionary", {})

    def _extract(self, text, *args, **kwargs):
        pass
