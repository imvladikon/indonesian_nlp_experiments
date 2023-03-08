#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

from indonesian_ie.base_extractor import BaseExtractor
from indonesian_ie.mentions_extractor import MentionExtractor
from indonesian_ie.nli_reranker import CrossEncoderEntailmentReranker
from indonesian_ie.qa_extractor import QAExtractor


DEFAULT_NLI_RELATION_PATTERNS = {
    "org:founded": {
        ("ORG", "DATE"): [
            # "{subject} was founded in {object}.",
            "{subject} didirikan pada {object}."
            # "founded date of {subject} is {object}.",
            "tanggal didirikan {subject} adalah {object}."
        ]
    },
    "per:date_of_birth": {
        ("PER", "DATE"): [
            # "{subject} was born on {object}."
            "{subject} lahir pada {object}."
            # "date of birth of {subject} is {object}."
            "tanggal lahir {subject} adalah {object}."
        ]
    },
    "per:age": {
        ("PER", "DATE"): [
            # "{subject} is {object} years old."
            "{subject} berusia {object} tahun."
        ]
    },
    "per:country_of_birth": {
        ("PER", "LOC"): [
            # "{subject} was born in {object}."
            "{subject} lahir di {object}.",
            # "{subject} is from {object}."
            "{subject} berasal dari {object}."
        ]
    },
    "org:website": {
        ("ORG", "URL"): [
            # "{subject} website is {object}."
            "website {subject} adalah {object}."
        ]
    },
    "per:employee_of": {
        ("PER", "ORG"): [
            # "{subject} works for {object}."
            "{subject} bekerja di {object}."
        ]
    },
    "NA": {
        ("*", "*"): [
            # "{subject} and {object} are not related."
            "{subject} dan {object} tidak berhubungan."
        ]
    },
    "per:city_of_birth": {
        ("PER", "LOC"): [
            # "{subject} was born in {object}."
            "{subject} lahir di {object}.",
        ]
    },
    "org:political/religious_affiliation": {
        ("ORG", "ORG"): [
            # "{subject} is affiliated with {object}."
            "{subject} beraffiliasi dengan {object}.",
            # "{subject} is a member of {object}."
            "{subject} adalah anggota dari {object}."
        ]
    },
    "org:members": {
        ("ORG", "PER"): [
            # "{subject} has {object} as a member."
            "{subject} memiliki {object} sebagai anggota.",
            # "{object} is working for {subject}."
            "{object} bekerja di {subject}."
        ]
    },
    "org:alternate_names": {
        ("ORG", "ORG"): [
            # "{subject} is also known as {object}."
            "{subject} juga dikenal sebagai {object}.",
            # "{object} is also known as {subject}."
            "{object} juga dikenal sebagai {subject}."
        ]
    },
    "org:member_of": {
        ("ORG", "ORG"): [
            # "{subject} is a member of {object}."
            "{subject} adalah anggota dari {object}.",
            # "{subject} is a part of {object}."
            "{subject} adalah bagian dari {object}."
        ]
    },
    "per:origin": {
        ("PER", "LOC"): [
            # "{subject} is from {object}."
            "{subject} berasal dari {object}.",
            # "{subject} is a citizen of {object}."
            "{subject} adalah warga negara {object}."
        ]
    },
    "per:title": {
        ("PER", "TITLE"): [
            # "{subject} is a {object}."
            "{subject} adalah seorang {object}."
        ]
    },
    "per:alternate_names": {
        ("PER", "PER"): [
            # "{subject} is also known as {object}."
            "{subject} juga dikenal sebagai {object}.",
            # "{object} is also known as {subject}."
            "{object} juga dikenal sebagai {subject}."
        ]
    },
    "per:event": {
        ("PER", "EVT"): [
            # "{subject} was involved in {object}."
            "{subject} terlibat dalam {object}."
        ],
        ("PER", "EVENT"): [
            # "{subject} was involved in {object}."
            "{subject} terlibat dalam {object}."
        ],
        ("PER", "MEETING"): [
            # "{subject} was involved in {object}."
            "{subject} terlibat dalam {object}."
        ]
    },
    "per:roles": {
        ("PER", "ROLE"): [
            # "{subject} is working as a {object}."
            "{subject} bekerja sebagai {object}."
        ]
    },
    "per:phone": {
        ("PER", "PHONE"): [
            "nomor telepon {subject} adalah {object}.",
            "nomor telepon {object} adalah {subject}."
        ]
    },
    "per:social_media": {
        ("PER", "SOCIAL_MEDIA"): [
         "akun {subject} di {object} adalah {object}.",
        ]
    },
    "per:email": {
        ("PER", "EMAIL"): [
            "email {subject} adalah {object}.",
            "email {object} adalah {subject}."
        ]
    },
    "per:credit_card": {
        ("PER", "CREDIT_CARD"): [
            "nomor kartu kredit {subject} adalah {object}.",
            "nomor kartu kredit {object} adalah {subject}."
        ]
    },
}

class RelationsQAExtractor(BaseExtractor):
    """
    Extracts relations between entities from text
    based on QA patterns and dictionary of relations
    """

    def __init__(self,
                 relations_patterns: Optional[Dict] = None,
                 n_jobs: int = 1,
                 **kwargs):
        super().__init__(**kwargs)
        self.n_jobs = n_jobs
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
                    # "Apakah {subject} adalah {object}?",
                    # "Is {subject} a coworker of {object}?",
                    # "Apakah {subject} adalah rekan kerja {object}?",
                    # "Did {subject} and {object} cooperate?"
                    # "Apakah {subject} dan {object} bekerja sama?",
                    # How person {subject} is related to person {object}?
                    "Bagaimana hubungan {subject} dengan {object}?",
                    "Bagaimana hubungan {object} dengan {subject}?"
                ],
                ("PER", "LOC"): [
                    # "Is {subject} from {object}?",
                    # "Apakah {subject} berasal dari {object}?",
                    # "Is {subject} a citizen of {object}?",
                    # "Apakah {subject} adalah warga negara {object}?",
                    # "Is {subject} a resident of {object}?"
                    # "Apakah {subject} adalah penduduk {object}?",
                    # How person {subject} is related to location {object}?
                    "Bagaimana hubungan {subject} dengan lokasi {object}?",
                    "Bagaimana hubungan {object} dengan lokasi {subject}?",

                ],

                ("PER", "ORG"): [
                    # "Is {subject} a member of {object}?",
                    # "Apakah {subject} adalah anggota {object}?",
                    # How person {subject} is related to organization {object}?
                    "Bagaimana hubungan {subject} dengan organisasi {object}?",
                    "Bagaimana hubungan {object} dengan organisasi {subject}?",
                ],
            }
        # add symmetric patterns
        symmetric_patterns = {}
        for (subj_type, obj_type), patterns in self.relations_patterns.items():
            if (obj_type, subj_type) not in self.relations_patterns:
                symmetric_patterns[(obj_type, subj_type)] = patterns
        self.relations_patterns.update(symmetric_patterns)
        del symmetric_patterns

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
        relations = self.from_mentions(mentions, context=text)
        return relations

    def from_mentions(self, mentions, context):
        """
        Extracts relations between entities from mentions
        where mentions is a list of entities with their start and end index and entity type
        """
        relations = []
        def _iter_pairs():
            for subject in mentions:
                for object in mentions:
                    if subject != object and subject["word"].strip() != object["word"].strip():
                        yield subject, object

        with ThreadPoolExecutor(max_workers=self.n_jobs) as executor:
            futures = [executor.submit(self._extract_relation, subject, object, context)
                       for subject, object in _iter_pairs()]
            for future in as_completed(futures):
                relation = future.result()
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


class RelationsNLIExtractor(RelationsQAExtractor):

    """
    Extracts relations between entities from text
    based on NLI model
    Pipeline:
    1. Extract mentions from text
    2. Generate hypotheses for relations between entities using patterns
    3. Classify hypotheses using NLI model
    4. Extract relations from hypotheses
    """
    def __init__(self, n_jobs=1, **kwargs):
        super().__init__(n_jobs=n_jobs, **kwargs)
        self.relations_patterns = DEFAULT_NLI_RELATION_PATTERNS
        self.nli_retriever = CrossEncoderEntailmentReranker(attribute_getter=lambda x: x["hypothesis"])

    def _extract_relation(self, subject, object, context):
        hypothesises = self._generate_hypotheses(subject, object)
        hits = self.nli_retriever(hypothesises=hypothesises, premise=context)
        if hits:
            best_hypothesis = hits[0]
            best_hypothesis, score = best_hypothesis
            relation = {
                "relation": best_hypothesis["relation"],
                "score": score,
                "subject": best_hypothesis["subject"],
                "object": best_hypothesis["object"],
            }
        else:
            relation = None
        return relation

    def _generate_hypotheses(self, subject, object):
        hypotheses = []
        subject_type = subject["entity_group"]
        object_type = object["entity_group"]
        for relation in self.relations_patterns:
            if (subject_type, object_type) not in self.relations_patterns[relation]:
                continue

            for pattern in self.relations_patterns[relation][(subject_type, object_type)]:
                hypothesis = self._generate_hypothesis_for_pattern(subject, object, pattern)
                hypotheses.append({
                    "hypothesis": hypothesis,
                    "subject": subject,
                    "object": object,
                    "relation": relation,
                })
        return hypotheses

    def _generate_hypothesis_for_pattern(self, subject, object, pattern):
        subject_text = subject["word"]
        object_text = object["word"]
        hypothesis = pattern.format(subject=subject_text, object=object_text)
        return hypothesis


if __name__ == '__main__':
    from pprint import pprint

    pipeline = RelationsQAExtractor(n_jobs=1)
    text = """Raja Purnawarman adalah seorang mahasiswa di Universitas Indonesia, facebooknya adalah raja.purnawarman, nomor teleponnya adalah 08123456789, nomor sim cardnya adalah 1234567890, nomor kartu identi
    Saya tinggal di Jakarta. Saya adalah mahasiswa Universitas Indonesia.
    """
    pprint(pipeline(text))
    

    pipeline = RelationsNLIExtractor(n_jobs=1)
    pprint(pipeline(text))


    # text = """Raja Purnawarman adalah seorang mahasiswa di Universitas Indonesia, facebooknya adalah raja.purnawarman, nomor teleponnya adalah 08123456789, nomor sim cardnya adalah 1234567890, nomor kartu identi
    # Saya tinggal di Jakarta. Saya adalah mahasiswa Universitas Indonesia.
    # """
    # # text = """
    # # Einstein lahir di Jerman pada 14 Maret 1879. Ia adalah seorang ilmuwan yang sangat terkenal. Ia adalah seorang ahli fisika dan ahli matematika. Ia adalah seorang ahli teori relativitas. Ia adalah seorang ahli teori kuantum. Ia adalah seorang ahli teori grav
    # # """
    # for sentence in text.split("."):
    #     relations = pipeline(sentence)
    #     pprint(relations)
