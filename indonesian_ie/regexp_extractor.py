#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from typing import Dict, List

from indonesian_ie.base_extractor import BaseExtractor


class RegexpExtractor(BaseExtractor):
    """
    Extracts entities using regular expressions
    """

    def __init__(self, patterns: Dict[str, List], **kwargs):
        """
        Args:
            patterns (list): Dict of patterns where key is the entity name and value is the pattern
        """
        super().__init__(**kwargs)
        self.patterns = patterns
        self.regex_patterns = self._build_regex()

    def _build_regex(self):
        """
        Builds a regex from a list of patterns
        Args:
            patterns (list): List of patterns
        Returns:
            regex (str): Regular expression
        """
        patterns = defaultdict(list)
        for entity_type, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                patterns[entity_type].append(compiled_pattern)
        return patterns

    def _extract(self, text, *args, **kwargs):
        """
        Extracts entities from text using regular expressions
        Args:
            text (str): Text to extract entities from
        Returns:
            entities (list): List of entities
        """
        entities = []

        entities_tree = defaultdict(list)
        for entity_type, patterns in self.regex_patterns.items():
            sub_entities = self._extract_for(entity_type, patterns, text)
            entities_tree[entity_type].extend(sub_entities)
        # resolve overlapping entities, e.g. by prioritizing entities depending on their type
        entities = self._resolve_overlapping_entities(entities_tree)
        return entities

    def _extract_for(self, entity_type, patterns, text):
        # extract entities for list of patterns with same entity type
        # and resolve overlapping entities with longest match
        entities = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                entity = text[start:end]
                if entity:
                    entities.append(
                        {"word": entity, "entity_group": entity_type, "start": start,
                         "end": end}
                    )

        # merge consecutive entities
        entities = sorted(entities, key=lambda x: x['start'])
        merged_entities = []
        for i, entity in enumerate(entities):
            if i == 0:
                merged_entities.append(entity)
                continue
            if entity['start'] <= merged_entities[-1]['end'] and entity['entity_group'] == \
                    merged_entities[-1]['entity_group']:
                merged_entities[-1]['end'] = entity['end']
                merged_entities[-1]['word'] = text[merged_entities[-1]['start']:
                                                   merged_entities[-1]['end']]
            else:
                merged_entities.append(entity)

        return merged_entities

    def _resolve_overlapping_entities(self, entities_tree):
        """
        Resolves overlapping entities by prioritizing entities depending on their type
        Args:
            entities_tree (dict): Tree of entities
        Returns:
            entities (list): List of entities
        """
        entities = []
        for entity_type, entity_list in entities_tree.items():
            for entity in entity_list:
                if not entities:
                    entities.append(entity)
                    continue
                # check if entity overlaps with any other entity
                for i, e in enumerate(entities):
                    if entity['start'] <= e['end'] and entity['end'] >= e['start']:
                        # if entity overlaps with existing entity, replace existing entity with entity with higher priority
                        if self._entity_priority(entity_type) > self._entity_priority(
                                e['entity_group']):
                            entities[i] = entity
                        break
                else:
                    entities.append(entity)
        return entities

    def _entity_priority(self, entity_type):
        """
        Returns the priority of an entity type
        Args:
            entity_type (str): Entity type
        Returns:
            priority (int): Priority of entity type
        """
        if entity_type == 'person':
            return 4
        elif entity_type == 'location':
            return 3
        elif entity_type == 'date':
            return 2
        elif entity_type == 'social_media':
            return 1
        else:
            return 0


class RegexpRulesEntityExtractor(RegexpExtractor):
    """
    Extracts entities using predefined regular expressions
    """

    def __init__(self, **kwargs):
        patterns = {
            "DATE": [
                r'\d{1,2}\/\d{1,2}\/\d{2,4}',
                r'\d{4}-\d{1,2}-\d{1,2}',
                # '(\d{1,2}[- /.](0?[1-9]|1[012]))',
                "((0?[1-9]|[12][0-9]|3[01])[- /.](0?[1-9]|1[012])[- /.](19|20)\\d\\d)",
                "((0?[1-9]|[12][0-9]|3[01])[- /.](0?[1-9]|1[012])[- /.]\\d\\d)",
                "([0-1]?[0-9]|2[0-3]):[0-5][0-9]",
                # yyyy
                r'20\d{2}',
                r'19\d{2}',
                r'.20\d{2}',
                r'.19\d{2}',
                r"19\d\d|20\d\d",
                r"19\d\d01|20\d\d01|19\d\d02|20\d\d02|19\d\d03|20\d\d03|19\d\d04|20\d\d04|19\d\d05|20\d\d05|19\d\d06|20\d\d06|19\d\d07|20\d\d07|19\d\d08|20\d\d08|19\d\d09|20\d\d09|19\d\d10|20\d\d10|19\d\d11|20\d\d11|19\d\d12|20\d\d12",
                r"19\d\d01[0123]\d|20\d\d01[0123]\d|19\d\d02[0123]\d|20\d\d02[0123]\d|19\d\d03[0123]\d|20\d\d03[0123]\d|19\d\d04[0123]\d|20\d\d04[0123]\d|19\d\d05[0123]\d|20\d\d05[0123]\d|19\d\d06[0123]\d|20\d\d06[0123]\d|19\d\d07[0123]\d|20\d\d07[0123]\d|19\d\d08[0123]\d|20\d\d08[0123]\d|19\d\d09[0123]\d|20\d\d09[0123]\d|19\d\d10[0123]\d|20\d\d10[0123]\d|19\d\d11[0123]\d|20\d\d11[0123]\d|19\d\d12[0123]\d|20\d\d12[0123]\d",
            ],
            "PHONE": [
                # r"\d{3}-\d{3}-\d{4}",
                r"\+?([ -]?\d+)+|\(\d+\)([ -]\d+)",
                r'0\d{9}', r'0\d{1,2}-\d{7}', r'0\d{1,2}-\d{3}-\d{4}',
                r'62 \d{9}', r'62 \d{1,2}-\d{7}', r'62 \d{1,2}-\d{3}-\d{4}',
            ],
            "EMAIL": [
                r"[a-z0-9]+@[a-z0-9]+\.[a-z]+",
                r'[a-z][_a-z0-9-.]+@[a-z0-9-]+[a-z]+\.[^\s]{2,}',
            ],
            "HASHTAG": [r"#([a-zA-Z0-9_]+)"],
            "URL": [
                r"(http|https)://[a-zA-Z0-9./]+",
                r"www.[a-zA-Z0-9./]+",
                r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
                r"https?:[a-zA-Z0-9_.+-/#~]+ ",
            ],
            "PASSPORT": [
                r"([a-zA-Z]{2})\d{8}",
                r"([a-zA-Z]{2})\d{7}"
            ],
            "CRYPTOWALLET": [
                # ETH
                r"0x[a-fA-F0-9]{40}",
                r"0x[a-fA-F0-9]{42}",
                r"0x[a-fA-F0-9]{64}",
                # BTC
                r"1[a-km-zA-HJ-NP-Z1-9]{25,34}",
            ],
            "IMEI": [
                r"\d{15}",
            ],
            "CREDIT_CARD": [
                r"\d{4} \d{4} \d{4} \d{4}",
                r"\d{4}-\d{4}-\d{4}-\d{4}",
            ],
            "MAC_ADDRESS": [
                r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})",
            ],
            "LOC": [
                r"[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)",
            ],
            "IP_ADDRESS": [
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            ],
            "SOCIAL_MEDIA": [
                r"twitter.com\/[a-zA-Z0-9_]+",
                r"facebook.com\/[a-zA-Z0-9_]+",
                r"instagram.com\/[a-zA-Z0-9_]+",
                r"linkedin.com\/[a-zA-Z0-9_]+",
                r"t.me\/[a-zA-Z0-9_]+",
                r"youtube.com\/[a-zA-Z0-9_]+",
                r"pinterest.com\/[a-zA-Z0-9_]+",
                r"reddit.com\/[a-zA-Z0-9_]+",
                r"tiktok.com\/[a-zA-Z0-9_]+",
                r"twitch.tv\/[a-zA-Z0-9_]+",
                r"whatsapp.com\/[a-zA-Z0-9_]+",
                r"telegram.me\/[a-zA-Z0-9_]+",
                r"telegram.org\/[a-zA-Z0-9_]+",
                r"telegram.com\/[a-zA-Z0-9_]+",
            ]

        }
        super().__init__(patterns=patterns, **kwargs)

    def _remove_overlapping_entities(self, entities, spans_tree):
        """
        Removes overlapping entities with resolvement to the longest entity
        Args:
            entities (list): List of entities
            spans_tree (dict): Dictionary of spans
        Returns:
            entities (list): List of entities
        """
        sorted_spans = sorted(spans_tree.keys())
        for start in sorted_spans:
            for end, entity_type, entity in spans_tree[start]:
                for entity_ in entities:
                    if entity_["start"] == start and entity_["end"] == end:
                        continue
                    if entity_["start"] <= start and entity_["end"] >= end:
                        entities.remove(entity_)
        return entities


if __name__ == '__main__':
    extractor = RegexpRulesEntityExtractor()
    text = (
        "My email is h@gmail.com and my phone number is +62 361 222777"
        " and my hashtag is #hello and my url is https://www.google.com and my date is 2019-01-01"
    )
    print(extractor(text))
