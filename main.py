#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import spacy_udpipe


class MorphologicalAnalyzer:

    def __init__(self, lang="id"):
        spacy_udpipe.download(lang)
        self.nlp = spacy_udpipe.load(lang)

    def analyze(self, text):
        doc = self.nlp(text)
        return doc

    def print(self, doc):
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.dep_)

    def extract_numerical(self, doc):
        return [token.text for token in doc if token.pos_ == "NUM"]

    def extract_noun(self, doc):
        return [token.text for token in doc if token.pos_ == "NOUN"]

    def extract_verb(self, doc):
        return [token.text for token in doc if token.pos_ == "VERB"]

    def extract_adjective(self, doc):
        return [token.text for token in doc if token.pos_ == "ADJ"]

    def extract_adverb(self, doc):
        return [token.text for token in doc if token.pos_ == "ADV"]

    def extract_pronoun(self, doc):
        return [token.text for token in doc if token.pos_ == "PRON"]

    def extract_preposition(self, doc):
        return [token.text for token in doc if token.pos_ == "ADP"]

    def extract_name(self, doc):
        return [token.text for token in doc if token.pos_ == "PROPN"]

    def extract_date(self, doc):
        return [token.text for token in doc if token.pos_ == "DATE"]



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
ttd.
Dr. H. Yodi Martono Wahyunadi, S.H., M.H.
Halaman 6 dari 7 halaman. Putusan Nomor 229 PK/TUN/2022
"""

analyzer = MorphologicalAnalyzer()
doc = analyzer.analyze(text)
analyzer.print(doc)
print(analyzer.extract_numerical(doc))
print(analyzer.extract_noun(doc))
print(analyzer.extract_verb(doc))
print(analyzer.extract_adjective(doc))
print(analyzer.extract_adverb(doc))
print(analyzer.extract_pronoun(doc))
print(analyzer.extract_preposition(doc))
print(analyzer.extract_name(doc))
print(analyzer.extract_date(doc))


