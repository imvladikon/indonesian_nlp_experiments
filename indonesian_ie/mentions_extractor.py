#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from transformers import AutoModelForTokenClassification, AutoTokenizer, NerPipeline

from indonesian_ie.base_extractor import BaseExtractor
from indonesian_ie.regexp_extractor import RegexpRulesEntityExtractor


class MentionExtractor(BaseExtractor):

    def __init__(
        self,
        model_name: str = "bstds/id-roberta-ner",
        aggregation_strategy: str = "max",
        **kwargs
    ):
        super().__init__(**kwargs)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.pipeline = NerPipeline(
            model=model, tokenizer=tokenizer, aggregation_strategy=aggregation_strategy
        )
        self.rule_based_extractor = RegexpRulesEntityExtractor()

    def _extract(self, *args, **kwargs):
        """
        'CRD': Cardinal
        'DAT': Date
        'EVT': Event
        'FAC': Facility
        'GPE': Geopolitical Entity
        'LAW': Law Entity (such as Undang-Undang)
        'LOC': Location
        'MON': Money
        'NOR': Political Organization
        'ORD': Ordinal
        'ORG': Organization
        'PER': Person
        'PRC': Percent
        'PRD': Product
        'QTY': Quantity
        'REG': Religion
        'TIM': Time
        'WOA': Work of Art
        'LAN': Language
        """
        text = args[0]
        mentions = self.pipeline(*args, **kwargs)
        tags_mapping = {
            "DAT": "DATE",
            "GPE": "LOC",
            "NOR": "ORG",
            "TIM": "DATE",
        }
        # fix the word
        for mention in mentions:
            mention["word"] = text[mention["start"] : mention["end"]]
            mention["entity_group"] = tags_mapping.get(
                mention["entity_group"], mention["entity_group"]
            )

        rule_based_mentions = self.rule_based_extractor(*args, **kwargs)

        for rule_based_mention in rule_based_mentions:
            for mention in mentions:
                if (
                    rule_based_mention["start"] >= mention["start"]
                    and rule_based_mention["end"] <= mention["end"]
                ):
                    break
            else:
                mentions.append(rule_based_mention)
        return mentions


if __name__ == '__main__':
    text = """
    tentang Peradilan Tata Usaha Negara sebagaimana telah diubah dengan
Undang-Undang Nomor 9 Tahun 2004 dan perubahan kedua dengan
Undang-Undang Nomor 51 Tahun 2009, serta peraturan perundang-
undangan lain yang terkait;
MENGADILI:
1. Menolak permohonan peninjauan kembali dari Pemohon Peninjauan
Kembali UMARDANI SUAT;
2. Menghukum Pemohon Peninjauan Kembali membayar biaya perkara
pada peninjauan kembali sejumlah Rp2.500.000,00 (dua juta lima ratus
ribu Rupiah);
Demikianlah diputuskan dalam rapat permusyawaratan Majelis Hakim
pada hari Kamis, tanggal 22 Desember 2022, oleh Dr. Irfan Fachruddin, S.H.,
C.N., Hakim Agung yang ditetapkan oleh Ketua Mahkamah Agung sebagai
Ketua Majelis, bersama-sama dengan Dr. Cerah Bangun, S.H., M.H. dan Dr.
H. Yodi Martono Wahyunadi, S.H., M.H., Hakim-Hakim Agung sebagai
Anggota, dan diucapkan dalam sidang terbuka untuk umum pada hari itu
juga oleh Ketua Majelis dengan dihadiri Hakim-Hakim Anggota tersebut, dan
Dewi Asimah, S.H., M.H., Panitera Pengganti tanpa dihadiri oleh para pihak.
Anggota Majelis: Ketua Majelis,
ttd. ttd.
Dr. Cerah Bangun, S.H., M.H. Dr. Irfan Fachruddin, S.H., C.N.
    """.strip()
    extractor = MentionExtractor()
    print(extractor(text))
