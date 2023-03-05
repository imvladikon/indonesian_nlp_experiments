#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from extractors.base_extractor import BaseExtractor
from extractors.mentions_extractor import MentionExtractor
from extractors.qa_extractor import QAExtractor


class RelationsExtractor(BaseExtractor):
    """
    Extracts relations between entities from text
    based on QA patterns and dictionary of relations
    using dictionary-trie data structure
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dictionary = kwargs.get("dictionary", {})
        self._mentions_extractor = None
        self._qa_extractor = None
        # list of patterns for relations between entities with QA prompts
        # patterns are symmetric
        self.relations_patterns = {
            ("PER", "PER"): [
                "Is {subject} an associate of {object}?",
                "Is {subject} a coworker of {object}?",
                "Did {subject} and {object} cooperate?"
            ],
            ("PER", "LOC"): [
                "Is {subject} from {object}?",
                "Is {subject} a citizen of {object}?",
                "Is {subject} a resident of {object}?"],
            ("PER", "ORG"): [
                "Is {subject} a member of {object}?",
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
            self._qa_extractor = QAExtractor()
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
                relation = self._extract_relation_for_pattern(subject, object, pattern, context)
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
    pipeline = RelationsExtractor()
    text = "Raja Purnawarman adalah seorang mahasiswa di Universitas Indonesia. Saya tinggal di Jakarta. Saya adalah mahasiswa Universitas Indonesia."
    relations = pipeline(text)
    print(relations)