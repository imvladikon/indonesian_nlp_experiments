#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class BaseExtractor:
    def __init__(self, **kwargs):
        pass

    def _extract(self, text, **kwargs):
        pass

    def __call__(self, **kwargs):
        return self._extract(**kwargs)