#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class MorphSentenceTokenizer:

    def __init__(self, lang="id", *args, **kwargs):
        try:
            import spacy_udpipe
            from spacy_udpipe import UDPipeModel
        except:
            print("Please install spacy_udpipe first")

        try:
            spacy_udpipe.download(lang)
            self.nlp = spacy_udpipe.load(lang)
            self.udpipe_model = UDPipeModel(lang)
            self.mode = kwargs.get("mode", "sentence")
        except:
            print("Please install spacy_udpipe first")

    def __call__(self, *args, **kwargs):
        return self._tokenize(*args, **kwargs)

    def _sentence_tokenize(self, text, *args, **kwargs):
        sentences = []
        for sentence in self.udpipe_model(text):
            sentences.append(sentence.getText())
        return sentences

    def _token_tokenize(self, text, *args, **kwargs):
        tokens = []
        for token in self.nlp(text):
            tokens.append(token)
        return tokens

    def _tokenize(self, text, *args, **kwargs):
        if self.mode == "sentence":
            return self._sentence_tokenize(text, *args, **kwargs)
        else:
            return self._token_tokenize(text, *args, **kwargs)

if __name__ == '__main__':
    sentence_tokenizer = MorphSentenceTokenizer(mode="token")
    for token in sentence_tokenizer("Saya ingin makan nasi. Saya ingin minum air."):
        print(token.text, token.lemma_, token.pos_, token.dep_, token.ent_type_)

    sentence_tokenizer = MorphSentenceTokenizer(mode="sentence")
    for sentence in sentence_tokenizer("Saya ingin makan nasi. Saya ingin minum air."):
        print(sentence)
