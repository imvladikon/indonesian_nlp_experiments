#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from transformers import AutoModelForTokenClassification, AutoTokenizer, NerPipeline

from extractors.base_extractor import BaseExtractor


class MentionExtractor(BaseExtractor):

    def __init__(
        self,
        model_name: str = "cahya/xlm-roberta-large-indonesian-NER",
        aggregation_strategy: str = "max",
        **kwargs
    ):
        super().__init__(**kwargs)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.pipeline = NerPipeline(
            model=model, tokenizer=tokenizer, aggregation_strategy=aggregation_strategy
        )

    def _extract(self, *args, **kwargs):
        text = args[0]
        mentions = self.pipeline(*args, **kwargs)
        # fix the word
        for mention in mentions:
            mention["word"] = text[mention["start"] : mention["end"]]
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
