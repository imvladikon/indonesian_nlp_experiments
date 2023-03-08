#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Callable, Optional, Sequence, Union

import torch

import numpy as np
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class CrossEncoderEntailmentReranker:

    def __init__(
        self,
        model_name_or_path: str = 'w11wo/indonesian-roberta-base-indonli',
        device: str = 'cpu',
        attribute_getter: Callable = lambda x: x,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.cross_encoder = AutoModelForSequenceClassification.from_pretrained(
            model_name_or_path
        )
        self.label2id = self.cross_encoder.config.label2id
        self.id2label = self.cross_encoder.config.id2label
        self.entailment_weights = {
            self.label2id['entailment']: 1,
            self.label2id['neutral']: 0.5,
            self.label2id['contradiction']: 0.0,
        }
        self.softmax = torch.nn.Softmax(dim=1)
        self.attribute_getter = attribute_getter

    def __call__(self, *args, **kwargs):
        return self._rerank(*args, **kwargs)

    @torch.inference_mode()
    def _rerank(
        self,
        premise: str,
        hypothesises: Sequence[str],
        threshold: float = 0.6,
        top_k: int = 1,
        **kwargs
    ) -> Sequence:
        if not hypothesises:
            return []
        cross_data = [
            (premise, self.attribute_getter(hypothesis)) for hypothesis in hypothesises
        ]
        encoded_input = self.tokenizer(
            cross_data,
            padding=True,
            truncation=True,
            return_tensors='pt',
        )
        logits = self.cross_encoder(**encoded_input)[0]
        probs = self.softmax(logits)
        indexes = torch.argmax(probs, dim=1)
        weights = [self.entailment_weights[idx.item()] for idx in indexes]
        scores = torch.max(probs, dim=1)[0] * torch.tensor(weights)
        indexes = torch.topk(scores, k=len(hypothesises), dim=0)[1]
        ret = [(hypothesises[idx.item()], scores[idx.item()].item()) for idx in indexes]
        if not ret:
            return []
        top_k = min(top_k, len(ret))
        return list(filter(lambda x: x[1] >= threshold, ret))[:top_k]


if __name__ == '__main__':
    from pprint import pprint

    reranker = CrossEncoderEntailmentReranker(
        model_name_or_path='w11wo/indonesian-roberta-base-indonli',
        attribute_getter=lambda x: x['fact'],
    )
    query = "Jakarta adalah ibu kota dari Indonesia."
    hits = [
        {"entity_id": "0", "fact": "Jakarta adalah ibu kota dari Indonesia."},
        {"entity_id": "1", "fact": "Indonesia adalah sebuah negara di Asia."},
        {"entity_id": "2", "fact": "Ottawa adalah ibu kota dari Indonesia."},
        {"entity_id": "3", "fact": "Indonesia adalah sebuah kota di Asia."},
        {"entity_id": "4", "fact": "Tidak ada ibu kota dari Indonesia."},
    ]
    pprint(reranker.rerank(query, hits))
