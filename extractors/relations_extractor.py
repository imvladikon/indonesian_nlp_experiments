#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Dict, Optional

from extractors.base_extractor import BaseExtractor
from extractors.extractive_qa_extractor import ExtractiveQAExtractor
from extractors.mentions_extractor import MentionExtractor
from extractors.qa_extractor import QAExtractor


class RelationsExtractor(BaseExtractor):
    """
    Extracts relations between entities from text
    based on QA patterns and dictionary of relations
    """

    def __init__(self, relations_patterns: Optional[Dict] = None, **kwargs):
        super().__init__(**kwargs)
        self._dictionary = kwargs.get("dictionary", {})
        self._mentions_extractor = None
        self._qa_extractor = None
        # list of patterns for relations between entities with QA prompts
        # patterns are symmetric
        if relations_patterns:
            self.relations_patterns = relations_patterns
        else:
            self.relations_patterns = {
                ("PER", "PER"): [
                    # "Is {subject} an associate of {object}?",
                    "Apakah {subject} adalah {object}?",
                    # "Is {subject} a coworker of {object}?",
                    "Apakah {subject} adalah rekan kerja {object}?",
                    # "Did {subject} and {object} cooperate?"
                    "Apakah {subject} dan {object} bekerja sama?",
                ],
                ("PER", "LOC"): [
                    # "Is {subject} from {object}?",
                    "Apakah {subject} berasal dari {object}?",
                    # "Is {subject} a citizen of {object}?",
                    "Apakah {subject} adalah warga negara {object}?",
                    # "Is {subject} a resident of {object}?"
                    "Apakah {subject} adalah penduduk {object}?",
                ],

                ("PER", "ORG"): [
                    # "Is {subject} a member of {object}?",
                    "Apakah {subject} adalah anggota {object}?",
                ],
            }

    @property
    def mentions_extractor(self):
        if not self._mentions_extractor:
            self._mentions_extractor = MentionExtractor()
        return self._mentions_extractor

    @property
    def qa_extractor(self):
        if not self._qa_extractor:
            self._qa_extractor = ExtractiveQAExtractor()
        return self._qa_extractor

    def _extract(self, text, *args, **kwargs):
        """
        Extracts relations between entities from text
        """
        mentions = self.mentions_extractor(text)
        relations = self.from_mentions(mentions)
        return relations

    def from_mentions(self, mentions):
        """
        Extracts relations between entities from mentions
        where mentions is a list of entities with their start and end index and entity type
        """
        relations = []
        for subject in mentions:
            for object in mentions:
                if subject != object:
                    relation = self._extract_relation(subject, object, context=text)
                    if relation:
                        relations.append(relation)
        return relations

    def _extract_relation(self, subject, object, context):
        """
        Extracts relation between two entities
        """
        relation = None
        subject_type = subject["entity_group"]
        object_type = object["entity_group"]
        if (subject_type, object_type) in self.relations_patterns:
            for pattern in self.relations_patterns[(subject_type, object_type)]:
                relation = self._extract_relation_for_pattern(subject, object, pattern,
                                                              context)
                if relation:
                    break
        return relation

    def _extract_relation_for_pattern(self, subject, object, pattern, context):
        """
        Extracts relation between two entities for a given pattern
        """
        relation = None
        subject_text = subject["word"]
        object_text = object["word"]
        question = pattern.format(subject=subject_text, object=object_text)
        answer = self.qa_extractor(question=question, context=context)
        if answer:
            relation = {
                "subject": subject,
                "object": object,
                "relation": answer,
            }
        return relation


if __name__ == '__main__':
    from pprint import pprint

    pipeline = RelationsExtractor()
    text = "Raja Purnawarman adalah seorang mahasiswa di Universitas Indonesia. Saya tinggal di Jakarta. Saya adalah mahasiswa Universitas Indonesia."
    relations = pipeline(text)
    pprint(relations)
    """
    [{'object': {'end': 56,
             'entity_group': 'ORG',
             'score': 0.99636495,
             'start': 44,
             'word': ' Universitas'},
  'relation': {'answer': 'Universitas Indonesia',
               'end': 66,
               'score': 0.27503731846809387,
               'start': 45},
  'subject': {'end': 16,
              'entity_group': 'PER',
              'score': 0.99897766,
              'start': 0,
              'word': 'Raja Purnawarman'}},
 {'object': {'end': 137,
             'entity_group': 'ORG',
             'score': 0.9853031,
             'start': 114,
             'word': ' Universitas Indonesia.'},
  'relation': {'answer': 'mahasiswa',
               'end': 41,
               'score': 0.34289419651031494,
               'start': 32},
  'subject': {'end': 16,
              'entity_group': 'PER',
              'score': 0.99897766,
              'start': 0,
              'word': 'Raja Purnawarman'}}]
    """
