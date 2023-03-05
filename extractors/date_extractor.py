#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# based on datefinder
from extractors.base_extractor import BaseExtractor
import copy
import logging
import regex as re
from dateutil import tz, parser

logger = logging.getLogger("datefinder")

NUMBERS_PATTERN = r"first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth"
NUMBERS_PATTERN += r"|pertama|kedua|ketiga|keempat|kelima|keenam|ketujuh|kedelapan|kesembilan|kesepuluh"
POSITIONNAL_TOKENS = r"next|last"
DIGITS_PATTERN = r"\d+"
DIGITS_SUFFIXES = r"st|th|rd|nd"
DAYS_PATTERN = "monday|tuesday|wednesday|thursday|friday|saturday|sunday|mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag|mon|tue|tues|wed|thu|thur|thurs|fri|sat|sun|man|tir|tirs|ons|tor|tors|fre|lør|søn"
DAYS_PATTERN += "|senin|selasa|rabu|kamis|jumat|sabtu|minggu"
MONTHS_PATTERN = r"january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|januar|februar|marts|april|maj|juni|juli|august|september|oktober|november|december|jan\.?|ene\.?|feb\.?|mar\.?|apr\.?|abr\.?|may\.?|maj\.?|jun\.?|jul\.?|aug\.?|ago\.?|sep\.?|sept\.?|oct\.?|okt\.?|nov\.?|dec\.?|dic\.?"
MONTHS_PATTERN += "|januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember"
TIMEZONES_PATTERN = "ACDT|ACST|ACT|ACWDT|ACWST|ADDT|ADMT|ADT|AEDT|AEST|AFT|AHDT|AHST|AKDT|AKST|AKTST|AKTT|ALMST|ALMT|AMST|AMT|ANAST|ANAT|ANT|APT|AQTST|AQTT|ARST|ART|ASHST|ASHT|AST|AWDT|AWST|AWT|AZOMT|AZOST|AZOT|AZST|AZT|BAKST|BAKT|BDST|BDT|BEAT|BEAUT|BIOT|BMT|BNT|BORT|BOST|BOT|BRST|BRT|BST|BTT|BURT|CANT|CAPT|CAST|CAT|CAWT|CCT|CDDT|CDT|CEDT|CEMT|CEST|CET|CGST|CGT|CHADT|CHAST|CHDT|CHOST|CHOT|CIST|CKHST|CKT|CLST|CLT|CMT|COST|COT|CPT|CST|CUT|CVST|CVT|CWT|CXT|ChST|DACT|DAVT|DDUT|DFT|DMT|DUSST|DUST|EASST|EAST|EAT|ECT|EDDT|EDT|EEDT|EEST|EET|EGST|EGT|EHDT|EMT|EPT|EST|ET|EWT|FET|FFMT|FJST|FJT|FKST|FKT|FMT|FNST|FNT|FORT|FRUST|FRUT|GALT|GAMT|GBGT|GEST|GET|GFT|GHST|GILT|GIT|GMT|GST|GYT|HAA|HAC|HADT|HAE|HAP|HAR|HAST|HAT|HAY|HDT|HKST|HKT|HLV|HMT|HNA|HNC|HNE|HNP|HNR|HNT|HNY|HOVST|HOVT|HST|ICT|IDDT|IDT|IHST|IMT|IOT|IRDT|IRKST|IRKT|IRST|ISST|IST|JAVT|JCST|JDT|JMT|JST|JWST|KART|KDT|KGST|KGT|KIZST|KIZT|KMT|KOST|KRAST|KRAT|KST|KUYST|KUYT|KWAT|LHDT|LHST|LINT|LKT|LMT|LMT|LMT|LMT|LRT|LST|MADMT|MADST|MADT|MAGST|MAGT|MALST|MALT|MART|MAWT|MDDT|MDST|MDT|MEST|MET|MHT|MIST|MIT|MMT|MOST|MOT|MPT|MSD|MSK|MSM|MST|MUST|MUT|MVT|MWT|MYT|NCST|NCT|NDDT|NDT|NEGT|NEST|NET|NFT|NMT|NOVST|NOVT|NPT|NRT|NST|NT|NUT|NWT|NZDT|NZMT|NZST|OMSST|OMST|ORAST|ORAT|PDDT|PDT|PEST|PET|PETST|PETT|PGT|PHOT|PHST|PHT|PKST|PKT|PLMT|PMDT|PMMT|PMST|PMT|PNT|PONT|PPMT|PPT|PST|PT|PWT|PYST|PYT|QMT|QYZST|QYZT|RET|RMT|ROTT|SAKST|SAKT|SAMT|SAST|SBT|SCT|SDMT|SDT|SET|SGT|SHEST|SHET|SJMT|SLT|SMT|SRET|SRT|SST|STAT|SVEST|SVET|SWAT|SYOT|TAHT|TASST|TAST|TBIST|TBIT|TBMT|TFT|THA|TJT|TKT|TLT|TMT|TOST|TOT|TRST|TRT|TSAT|TVT|ULAST|ULAT|URAST|URAT|UTC|UYHST|UYST|UYT|UZST|UZT|VET|VLAST|VLAT|VOLST|VOLT|VOST|VUST|VUT|WARST|WART|WAST|WAT|WDT|WEDT|WEMT|WEST|WET|WFT|WGST|WGT|WIB|WIT|WITA|WMT|WSDT|WSST|WST|WT|XJT|YAKST|YAKT|YAPT|YDDT|YDT|YEKST|YEKST|YEKT|YEKT|YERST|YERT|YPT|YST|YWT|zzz"
## explicit north american timezones that get replaced
NA_TIMEZONES_PATTERN = "pacific|eastern|mountain|central"
ALL_TIMEZONES_PATTERN = TIMEZONES_PATTERN + "|" + NA_TIMEZONES_PATTERN
DELIMITERS_PATTERN = r"[/\:\-\,\s\_\+\@]+"

# Allows for straightforward datestamps e.g 2017, 201712, 20171223. Created with:
#  YYYYMM_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'|20\d\d'+'{:0>2}'.format(mon) for mon in range(1, 13)])
#  YYYYMMDD_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'[0123]\d|20\d\d'+'{:0>2}'.format(mon)+'[0123]\d' for mon in range(1, 13)])
YYYY_PATTERN = r"19\d\d|20\d\d"
YYYYMM_PATTERN = r"19\d\d01|20\d\d01|19\d\d02|20\d\d02|19\d\d03|20\d\d03|19\d\d04|20\d\d04|19\d\d05|20\d\d05|19\d\d06|20\d\d06|19\d\d07|20\d\d07|19\d\d08|20\d\d08|19\d\d09|20\d\d09|19\d\d10|20\d\d10|19\d\d11|20\d\d11|19\d\d12|20\d\d12"
YYYYMMDD_PATTERN = r"19\d\d01[0123]\d|20\d\d01[0123]\d|19\d\d02[0123]\d|20\d\d02[0123]\d|19\d\d03[0123]\d|20\d\d03[0123]\d|19\d\d04[0123]\d|20\d\d04[0123]\d|19\d\d05[0123]\d|20\d\d05[0123]\d|19\d\d06[0123]\d|20\d\d06[0123]\d|19\d\d07[0123]\d|20\d\d07[0123]\d|19\d\d08[0123]\d|20\d\d08[0123]\d|19\d\d09[0123]\d|20\d\d09[0123]\d|19\d\d10[0123]\d|20\d\d10[0123]\d|19\d\d11[0123]\d|20\d\d11[0123]\d|19\d\d12[0123]\d|20\d\d12[0123]\d"
YYYYMMDDHHMMSS_PATTERN = "|".join(
    [
        r"19\d\d"
        + "{:0>2}".format(mon)
        + r"[0-3]\d[0-5]\d[0-5]\d[0-5]\d|20\d\d"
        + "{:0>2}".format(mon)
        + r"[0-3]\d[0-5]\d[0-5]\d[0-5]\d"
        for mon in range(1, 13)
    ]
)
ISO8601_PATTERN = r"(?P<years>-?(\:[1-9][0-9]*)?[0-9]{4})\-(?P<months>1[0-2]|0[1-9])\-(?P<days>3[01]|0[1-9]|[12][0-9])T(?P<hours>2[0-3]|[01][0-9])\:(?P<minutes>[0-5][0-9]):(?P<seconds>[0-5][0-9])(?:[\.,]+(?P<microseconds>[0-9]+))?(?P<offset>(?:Z|[+-](?:2[0-3]|[01][0-9])\:[0-5][0-9]))?"
UNDELIMITED_STAMPS_PATTERN = "|".join(
    [YYYYMMDDHHMMSS_PATTERN, YYYYMMDD_PATTERN, YYYYMM_PATTERN, ISO8601_PATTERN]
)
DELIMITERS_PATTERN = r"[/\:\-\,\.\s\_\+\@]+"
TIME_PERIOD_PATTERN = r"a\.m\.|am|p\.m\.|pm"
## can be in date strings but not recognized by dateutils
EXTRA_TOKENS_PATTERN = r"due|by|on|during|standard|daylight|savings|time|date|dated|of|to|through|between|until|at|day"

## TODO: Get english numbers?
## http://www.rexegg.com/regex-trick-numbers-in-english.html

RELATIVE_PATTERN = "before|after|next|last|ago"
RELATIVE_PATTERN += "sebelum|sesudah|berikutnya|terakhir|yang lalu"
TIME_SHORTHAND_PATTERN = "noon|midnight|today|yesterday"
TIME_SHORTHAND_PATTERN += "siang|tengah malam|hari ini|kemarin"
UNIT_PATTERN = "second|minute|hour|day|week|month|year"
UNIT_PATTERN += "detik|menit|jam|hari|minggu|bulan|tahun"

## Time pattern is used independently, so specified here.
TIME_PATTERN = r"""
(?P<time>
    ## Captures in format XX:YY(:ZZ) (PM) (EST)
    (
        (?P<hours>\d{{1,2}})
        \:
        (?P<minutes>\d{{1,2}})
        (\:(?<seconds>\d{{1,2}}))?
        ([\.\,](?<microseconds>\d{{1,6}}))?
        \s*
        (?P<time_periods>{time_periods})?
        \s*
        (?P<timezones>{timezones})?
    )
    |
    ## Captures in format 11 AM (EST)
    ## Note with single digit capture requires time period
    (
        (?P<hours>\d{{1,2}})
        \s*
        (?P<time_periods>{time_periods})
        \s*
        (?P<timezones>{timezones})*
    )
)
""".format(
    time_periods=TIME_PERIOD_PATTERN, timezones=ALL_TIMEZONES_PATTERN
)

DATES_PATTERN = """
(
    ## Undelimited datestamps (treated independently)
    (?P<undelimited_stamps>{undelimited_stamps})
    |
    (
        {time}
        |
        ## Grab any four digit years
        (?P<years>{years})
        |
        ## Numbers
        (?P<numbers>{numbers})
        ## Grab any digits
        |
        (?P<digits>{digits})(?P<digits_suffixes>{digits_suffixes})?
        |
        (?P<days>{days})
        |
        (?P<months>{months})
        |
        ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
        ## as well as whitespace
        (?P<delimiters>{delimiters})
        |
        (?P<positionnal_tokens>{positionnal_tokens})
        |
        ## These tokens could be in phrases that dateutil does not yet recognize
        ## Some are US Centric
        (?P<extra_tokens>{extra_tokens})
    ## We need at least three items to match for minimal datetime parsing
    ## ie 10pm
    ){{1,1}}
)
"""

DATES_PATTERN = DATES_PATTERN.format(
    time=TIME_PATTERN,
    undelimited_stamps=UNDELIMITED_STAMPS_PATTERN,
    years=YYYY_PATTERN,
    numbers=NUMBERS_PATTERN,
    digits=DIGITS_PATTERN,
    digits_suffixes=DIGITS_SUFFIXES,
    days=DAYS_PATTERN,
    months=MONTHS_PATTERN,
    delimiters=DELIMITERS_PATTERN,
    positionnal_tokens=POSITIONNAL_TOKENS,
    extra_tokens=EXTRA_TOKENS_PATTERN,
)

ALL_GROUPS = [
    'time',
    'years',
    'numbers',
    'digits',
    'digits_suffixes',
    'days',
    'months',
    'delimiters',
    'positionnal_tokens',
    'extra_tokens',
    'undelimited_stamps',
    'hours',
    'minutes',
    'seconds',
    'microseconds',
    'time_periods',
    'timezones',
]

DATE_REGEX = re.compile(
    DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE
)

TIME_REGEX = re.compile(
    TIME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE
)

## These tokens can be in original text but dateutil
## won't handle them without modification
REPLACEMENTS = {
    "standard": " ",
    "daylight": " ",
    "savings": " ",
    "time": " ",
    "date": " ",
    "by": " ",
    "due": " ",
    "on": " ",
    "to": " ",
    "day": " ",
}

TIMEZONE_REPLACEMENTS = {
    "pacific": "PST",
    "eastern": "EST",
    "mountain": "MST",
    "central": "CST",
}

## Characters that can be removed from ends of matched strings
STRIP_CHARS = " \n\t:-.,_"

# split ranges
RANGE_SPLIT_PATTERN = r'\Wto\W|\Wthrough\W'

RANGE_SPLIT_REGEX = re.compile(
    RANGE_SPLIT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL
)


class DateFragment:

    def __init__(self):
        self.match_str = ''
        self.indices = (0, 0)
        self.captures = {}

    def __repr__(self):
        str_capt = ', '.join(
            ['"{}": [{}]'.format(c, self.captures[c]) for c in self.captures]
        )
        return '{} [{}, {}]\nCaptures: {}'.format(
            self.match_str, self.indices[0], self.indices[1], str_capt
        )

    def get_captures_count(self):
        return sum([len(self.captures[m]) for m in self.captures])


class DateFinder(object):
    """
    Locates dates in a text
    """

    def __init__(self, base_date=None, first="month"):
        self.base_date = base_date
        self.dayfirst = False
        self.yearfirst = False
        if first == "day":
            self.dayfirst = True
        if first == "year":
            self.yearfirst = True

    def find_dates(self,
                   text,
                   source=False,
                   index=False,
                   strict=False):
        for date_string, indices, captures in self.extract_date_strings(
                text, strict=strict
        ):
            as_dt = self.parse_date_string(date_string, captures)
            if as_dt is None:
                ## Dateutil couldn't make heads or tails of it
                ## move on to next
                continue

            returnables = (as_dt,)
            if source:
                returnables = returnables + (date_string,)
            if index:
                returnables = returnables + (indices,)

            if len(returnables) == 1:
                returnables = returnables[0]
            yield returnables

    def _find_and_replace(self, date_string, captures):
        """
        :warning: when multiple tz matches exist the last sorted capture will trump
        :param date_string:
        :return: date_string, tz_string
        """
        # add timezones to replace
        cloned_replacements = copy.copy(REPLACEMENTS)  # don't mutate
        for tz_string in captures.get("timezones", []):
            cloned_replacements.update({tz_string: " "})

        date_string = date_string.lower()
        for key, replacement in cloned_replacements.items():
            # we really want to match all permutations of the key surrounded by whitespace chars except one
            # for example: consider the key = 'to'
            # 1. match 'to '
            # 2. match ' to'
            # 3. match ' to '
            # but never match r'(\s|)to(\s|)' which would make 'october' > 'ocber'
            date_string = re.sub(
                r"(^|\s)" + key + r"(\s|$)",
                replacement,
                date_string,
                flags=re.IGNORECASE,
            )

        return date_string, self._pop_tz_string(sorted(captures.get("timezones", [])))

    def _pop_tz_string(self, list_of_timezones):
        try:
            tz_string = list_of_timezones.pop()
            # make sure it's not a timezone we
            # want replaced with better abbreviation
            return TIMEZONE_REPLACEMENTS.get(tz_string, tz_string)
        except IndexError:
            return ""

    def _add_tzinfo(self, datetime_obj, tz_string):
        """
        take a naive datetime and add dateutil.tz.tzinfo object

        :param datetime_obj: naive datetime object
        :return: datetime object with tzinfo
        """
        if datetime_obj is None:
            return None

        tzinfo_match = tz.gettz(tz_string)
        return datetime_obj.replace(tzinfo=tzinfo_match)

    def parse_date_string(self, date_string, captures):
        # For well formatted string, we can already let dateutils parse them
        # otherwise self._find_and_replace method might corrupt them
        try:
            as_dt = parser.parse(
                date_string,
                default=self.base_date,
                dayfirst=self.dayfirst,
                yearfirst=self.yearfirst,
            )
        except (ValueError, OverflowError):
            # replace tokens that are problematic for dateutil
            date_string, tz_string = self._find_and_replace(date_string, captures)

            ## One last sweep after removing
            date_string = date_string.strip(STRIP_CHARS)
            ## Match strings must be at least 3 characters long
            ## < 3 tends to be garbage
            if len(date_string) < 3:
                return None

            try:
                logger.debug("Parsing {0} with dateutil".format(date_string))
                as_dt = parser.parse(
                    date_string,
                    default=self.base_date,
                    dayfirst=self.dayfirst,
                    yearfirst=self.yearfirst,
                )
            except Exception as e:
                logger.debug(e)
                as_dt = None
            if tz_string:
                as_dt = self._add_tzinfo(as_dt, tz_string)
        return as_dt

    def extract_date_strings(self, text, strict=False):
        """
        Scans text for possible datetime strings and extracts them
        :param strict: Strict mode will only return dates sourced with day, month, and year
        """
        return self.extract_date_strings_inner(text, text_start=0, strict=strict)

    def extract_date_strings_inner(self, text, text_start=0, strict=False):
        """
        Extends extract_date_strings by text_start parameter: used in recursive calls to
        store true text coordinates in output
        """

        # Try to find ranges first
        rng = self.split_date_range(text)
        if rng and len(rng) > 1:
            range_strings = []
            for range_str in rng:
                range_strings.extend(
                    self.extract_date_strings_inner(
                        range_str[0], text_start=range_str[1][0], strict=strict
                    )
                )
            for range_string in range_strings:
                yield range_string
            return

        tokens = self.tokenize_string(text)
        items = self.merge_tokens(tokens)
        for match in items:
            match_str = match.match_str
            indices = (match.indices[0] + text_start, match.indices[1] + text_start)

            ## Get individual group matches
            captures = match.captures
            # time = captures.get('time')
            digits = captures.get("digits")
            # digits_modifiers = captures.get('digits_modifiers')
            # days = captures.get('days')
            months = captures.get("months")
            years = captures.get("years")
            # timezones = captures.get('timezones')
            # delimiters = captures.get('delimiters')
            # time_periods = captures.get('time_periods')
            # extra_tokens = captures.get('extra_tokens')

            if strict:
                complete = False
                if len(digits) == 3:  # 12-05-2015
                    complete = True
                elif (len(months) == 1) and (
                        len(digits) == 2
                ):  # 19 February 2013 year 09:10
                    complete = True
                elif (len(years) == 1) and (len(digits) == 2):  # 09/06/2018
                    complete = True

                elif (
                        (len(years) == 1) and (len(months) == 1) and (len(digits) == 1)
                ):  # '19th day of May, 2015'
                    complete = True

                if not complete:
                    continue

            ## sanitize date string
            ## replace unhelpful whitespace characters with single whitespace
            match_str = re.sub(r"[\n\t\s\xa0]+", " ", match_str)
            match_str = match_str.strip(STRIP_CHARS)

            ## Save sanitized source string
            yield match_str, indices, captures

    def tokenize_string(self, text):
        """
        Get matches from source text. Method merge_tokens will later compose
        potential date strings out of these matches.
        :param text: source text like 'the big fight at 2p.m. mountain standard time on ufc.com'
        :return: [(match_text, match_group, {match.capturesdict()}), ...]
        """
        items = []

        last_index = 0

        for match in DATE_REGEX.finditer(text):
            match_str = match.group(0)
            indices = match.span(0)
            captures = match.capturesdict()
            group = self.get_token_group(captures)

            if indices[0] > last_index:
                items.append((text[last_index: indices[0]], "", {}))
            items.append((match_str, group, captures))
            last_index = indices[1]
        if last_index < len(text):
            items.append((text[last_index: len(text)], "", {}))
        return items

    def merge_tokens(self, tokens):
        """
        Makes potential date strings out of matches, got from tokenize_string method.
        :param tokens: [(match_text, match_group, {match.capturesdict()}), ...]
        :return: potential date strings
        """
        MIN_MATCHES = 3
        fragments = []
        frag = DateFragment()

        start_char, total_chars = 0, 0

        for token in tokens:
            total_chars += len(token[0])

            tok_text, group, tok_capts = token[0], token[1], token[2]
            if not group:
                if frag.indices[1] > 0:
                    if frag.get_captures_count() >= MIN_MATCHES:
                        fragments.append(frag)
                frag = DateFragment()
                start_char = total_chars
                continue

            if frag.indices[1] == 0:
                frag.indices = (start_char, total_chars)
            else:
                frag.indices = (frag.indices[0], total_chars)  # -1

            frag.match_str += tok_text

            for capt in tok_capts:
                if capt in frag.captures:
                    frag.captures[capt] += tok_capts[capt]
                else:
                    frag.captures[capt] = tok_capts[capt]

            start_char = total_chars

        if frag.get_captures_count() >= MIN_MATCHES:  # frag.matches
            fragments.append(frag)

        for frag in fragments:
            for gr in ALL_GROUPS:
                if gr not in frag.captures:
                    frag.captures[gr] = []

        return fragments

    @staticmethod
    def get_token_group(captures):
        for gr in ALL_GROUPS:
            lst = captures.get(gr)
            if lst and len(lst) > 0:
                return gr
        return ""

    @staticmethod
    def split_date_range(text):
        st_matches = RANGE_SPLIT_REGEX.finditer(text)
        start = 0
        parts = []  # List[Tuple[str, Tuple[int, int]]]

        for match in st_matches:
            match_start = match.start()
            if match_start > start:
                parts.append((text[start:match_start], (start, match_start)))
            start = match.end()

        if start < len(text):
            parts.append((text[start:], (start, len(text))))

        return parts


class DateExtractor(BaseExtractor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _extract(self,
                 text,
                 base_date=None,
                 first="month",
                 *args, **kwargs):
        """
                Extract datetime strings from text

                :param text:
                    A string that contains one or more natural language or literal
                    datetime strings
                :type text: str|unicode
                :param source:
                    Return the original string segment
                :type source: boolean
                :param index:
                    Return the indices where the datetime string was located in text
                :type index: boolean
                :param strict:
                    Only return datetimes with complete date information. For example:
                    `July 2016` of `Monday` will not return datetimes.
                    `May 16, 2015` will return datetimes.
                :type strict: boolean
                :param base_date:
                    Set a default base datetime when parsing incomplete dates
                :type base_date: datetime
                :param first:
                    Whether to interpret the the first value in an ambiguous 3-integer date
                    (01/02/03) as the month, day, or year. Values can be `month`, `day`, `year`.
                    Default is `month`.
                :type first: str|unicode


                :return: Returns a generator that produces :mod:`datetime.datetime` objects,
                    or a tuple with the source text and index, if requested
        """
        date_finder = DateFinder(base_date=base_date, first=first)

        entities = []
        for _, (start, end) in date_finder.find_dates(text,
                                                      source=False,
                                                      index=True,
                                                      strict=False):
            span = text[start:end]
            entities.append({
                "word": span,
                "entity_group": "date",
                "start": start,
                "end": end
            })

        # merge consecutive entities
        entities = sorted(entities, key=lambda x: x['start'])
        merged_entities = []
        for i, entity in enumerate(entities):
            if i == 0:
                merged_entities.append(entity)
                continue
            if entity['start'] <= merged_entities[-1]['end'] and entity[
                'entity_group'] == \
                    merged_entities[-1]['entity_group']:
                merged_entities[-1]['end'] = entity['end']
                merged_entities[-1]['word'] = text[merged_entities[-1]['start']:
                                                   merged_entities[-1]['end']]
            else:
                merged_entities.append(entity)
        return merged_entities


if __name__ == "__main__":
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
    extractor = DateExtractor()
    print(extractor(text))
