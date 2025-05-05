"""
crate_anon/linkage/tests/fuzzy_id_match_tests.py

===============================================================================

    Copyright (C) 2015, University of Cambridge, Department of Psychiatry.
    Created by Rudolf Cardinal (rnc1001@cam.ac.uk).

    This file is part of CRATE.

    CRATE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CRATE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CRATE. If not, see <https://www.gnu.org/licenses/>.

===============================================================================

Unit tests.

"""

# =============================================================================
# Imports
# =============================================================================

import logging
import unittest
from typing import List, Optional, Tuple, Type

from cardinal_pythonlib.probability import probability_from_log_odds
from pendulum import Date

from crate_anon.linkage.comparison import (
    AdjustLogOddsComparison,
    Comparison,
    DirectComparison,
)
from crate_anon.linkage.constants import (
    FuzzyDefaults,
    GENDER_FEMALE,
    GENDER_MALE,
    GENDER_MISSING,
    GENDER_OTHER,
    INFINITY,
    VALID_GENDERS,
)
from crate_anon.linkage.frequencies import (
    BasicNameFreqInfo,
    NameFrequencyInfo,
    PostcodeFrequencyInfo,
)
from crate_anon.linkage.identifiers import (
    DateOfBirth,
    DummyLetterIdentifier,
    DummyLetterTemporalIdentifier,
    Forename,
    gen_best_comparisons,
    Gender,
    Identifier,
    PerfectID,
    Postcode,
    Surname,
    SurnameFragment,
    TemporalIDHolder,
)
from crate_anon.linkage.helpers import (
    get_postcode_sector,
    is_valid_isoformat_date,
    ln,
    POSTCODE_REGEX,
    remove_redundant_whitespace,
    safe_upper,
    simplify_punctuation_whitespace,
    standardize_name,
    standardize_postcode,
    surname_alternative_fragments,
)
from crate_anon.linkage.matchconfig import MatchConfig
from crate_anon.linkage.people import DuplicateIDError, People
from crate_anon.linkage.person import Person

log = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

BAD_DATE_STRINGS = ["1950-31-12", "1950", "blah", "2000-02-30"]
GOOD_DATE_STRINGS = ["1950-12-31", "1890-01-01", "2000-01-01"]
BAD_POSTCODES = [
    "99XX99",
    "CB99 9XXY",
    "CB99",
    "CB2",
    "NW19TTTEMP",
    "NW19TT TEMP",
]
GOOD_POSTCODES = [
    "CB99 9XY",
    "CB2 0QQ",
    "ZZ99 3VZ",
    "Z Z 9 9 3 V Z",
    " zz993vz ",
]  # good once standardized, anyway
BAD_GENDERS = ["Y", "male", "female", "?"]


# =============================================================================
# Rapid creation of a dummy config (without loading actual name/postcode info)
# =============================================================================


def mk_test_config(**kwargs) -> MatchConfig:
    """
    Create a dummy config, using dummy name/postcode info.
    """
    predefined_forenames = [
        BasicNameFreqInfo(
            name="ALICE",
            gender=GENDER_FEMALE,
            p_name=0.0032597245570899847,
            metaphone="ALK",
            p_metaphone=0.005664202032042135,
            p_metaphone_not_name=0.00240447747495215,
            f2c="AL",
            p_f2c=0.027635117202534115,
            p_f2c_not_name_metaphone=0.022541989771499515,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="BEATRICE",
            gender=GENDER_FEMALE,
            p_name=0.0011134697472956023,
            metaphone="PTRK",
            p_metaphone=0.010795171997297154,
            p_metaphone_not_name=0.009681702250001551,
            f2c="BE",
            p_f2c=0.020540629656206778,
            p_f2c_not_name_metaphone=0.01938862260342886,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="BETTY",
            gender=GENDER_FEMALE,
            p_name=0.005856056682186572,
            metaphone="PT",
            p_metaphone=0.007567968531021441,
            p_metaphone_not_name=0.0017119118488348687,
            f2c="BE",
            p_f2c=0.020540629656206778,
            p_f2c_not_name_metaphone=0.014031211254451567,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="BOB",
            gender=GENDER_MALE,
            p_name=0.0005341749908504777,
            metaphone="PP",
            p_metaphone=0.002569054271327976,
            p_metaphone_not_name=0.0020348792804774983,
            f2c="BO",
            p_f2c=0.0035610312205931094,
            p_f2c_not_name_metaphone=0.0010918026974037107,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="CAROLINE",
            gender=GENDER_FEMALE,
            p_name=0.001289812197195456,
            metaphone="KRLN",
            p_metaphone=0.005979308865585442,
            p_metaphone_not_name=0.004689496668389986,
            f2c="CA",
            p_f2c=0.033910941860871194,
            p_f2c_not_name_metaphone=0.02860674130257904,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="CELIA",
            gender=GENDER_FEMALE,
            p_name=0.0003141885536034312,
            metaphone="KL",
            p_metaphone=0.016359410337593906,
            p_metaphone_not_name=0.016045221783990475,
            f2c="CE",
            p_f2c=0.0030682294813082723,
            p_f2c_not_name_metaphone=0.0026663592268114434,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="DELILAH",
            gender=GENDER_FEMALE,
            p_name=0.00019936172952521078,
            metaphone="TLL",
            p_metaphone=0.000491534931894549,
            p_metaphone_not_name=0.00029217320236933826,
            f2c="DE",
            p_f2c=0.02472305974107954,
            p_f2c_not_name_metaphone=0.024435022377723725,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="DOROTHY",
            gender=GENDER_FEMALE,
            p_name=0.006484867451993301,
            metaphone="TR0",
            p_metaphone=0.007164437365410392,
            p_metaphone_not_name=0.0006795699134170908,
            f2c="DO",
            p_f2c=0.020044376270378746,
            p_f2c_not_name_metaphone=0.01298493890496824,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="ELIZABETH",
            gender=GENDER_FEMALE,
            p_name=0.009497275400440382,
            metaphone="ALSP",
            p_metaphone=0.010079561736620864,
            p_metaphone_not_name=0.0005822863361804823,
            f2c="EL",
            p_f2c=0.02543961854560152,
            p_f2c_not_name_metaphone=0.015404362973960957,
            synthetic=False,
        ),
    ]  # type: List[BasicNameFreqInfo]
    forename_freq_info = NameFrequencyInfo(
        csv_filename="",
        cache_filename="",
        by_gender=True,
        min_frequency=FuzzyDefaults.FORENAME_MIN_FREQ,
    )
    for f in predefined_forenames:
        forename_freq_info.name_gender_idx[f.name, f.gender] = f

    predefined_surnames = [
        BasicNameFreqInfo(
            name="JONES",
            gender="",
            p_name=0.00621,
            metaphone="JNS",
            p_metaphone=0.0068899999999999986,
            p_metaphone_not_name=0.0006799999999999983,
            f2c="JO",
            p_f2c=0.019480000000000268,
            p_f2c_not_name_metaphone=0.012984999999999938,
            synthetic=False,
        ),
        BasicNameFreqInfo(
            name="SMITH",
            gender="",
            p_name=0.01006,
            metaphone="SM0",
            p_metaphone=0.010129999999999998,
            p_metaphone_not_name=6.999999999999888e-05,
            f2c="SM",
            p_f2c=0.012514999999999967,
            p_f2c_not_name_metaphone=0.0023849999999999896,
            synthetic=False,
        ),
    ]  # type: List[BasicNameFreqInfo]
    surname_freq_info = NameFrequencyInfo(
        csv_filename="",
        cache_filename="",
        by_gender=False,
        min_frequency=FuzzyDefaults.SURNAME_MIN_FREQ,
    )
    for s in predefined_surnames:
        surname_freq_info.name_gender_idx[s.name, s.gender] = s

    postcode_freq_info = PostcodeFrequencyInfo(
        csv_filename="", cache_filename=""
    )

    return MatchConfig(
        forename_freq_info=forename_freq_info,
        surname_freq_info=surname_freq_info,
        postcode_freq_info=postcode_freq_info,
        **kwargs,
    )


# =============================================================================
# Helper class
# =============================================================================


class TestCondition:
    """
    Two representations of a person and whether they should match.
    """

    def __init__(
        self,
        cfg: MatchConfig,
        person_a: Person,
        person_b: Person,
        should_match: bool,
        debug: bool = True,
    ) -> None:
        """
        Args:
            cfg: the main :class:`MatchConfig` object
            person_a: one representation of a person
            person_b: another representation of a person
            should_match: should they be treated as the same person?
            debug: be verbose?
        """
        self.cfg = cfg
        self.person_a = person_a
        self.person_b = person_b
        self.should_match = should_match

        for id_person in (self.person_a, self.person_b):
            assert id_person.is_plaintext()
            id_person.ensure_valid_as_proband()
            for identifier in id_person.debug_gen_identifiers():
                assert identifier.is_plaintext

        log.info("- Making hashed versions for later")
        self.hashed_a = self.person_a.hashed()
        self.hashed_b = self.person_b.hashed()
        for h_person in (self.hashed_a, self.hashed_b):
            assert h_person.is_hashed()
            h_person.ensure_valid_as_proband()
            for identifier in h_person.debug_gen_identifiers():
                assert not identifier.is_plaintext
        self.debug = debug

    def log_odds_same_plaintext(self) -> float:
        """
        Checks whether the plaintext person objects match.

        Returns:
            float: the log odds that they are the same person
        """
        return self.person_a.log_odds_same(self.person_b)

    def log_odds_same_hashed(self) -> float:
        """
        Checks whether the hashed versions match.

        Returns:
            float: the log odds that they are the same person
        """
        return self.hashed_a.log_odds_same(self.hashed_b)

    def matches_plaintext(self) -> Tuple[bool, float]:
        """
        Do the plaintext versions match, by threshold?

        Returns:
            tuple: (matches, log_odds)
        """
        log_odds = self.log_odds_same_plaintext()
        return self.cfg.exceeds_primary_threshold(log_odds), log_odds

    def matches_hashed(self) -> Tuple[bool, float]:
        """
        Do the raw versions match, by threshold?

        Returns:
            bool: is there a match?
        """
        log_odds = self.log_odds_same_hashed()
        return self.cfg.exceeds_primary_threshold(log_odds), log_odds

    def check_comparison_as_expected(self) -> None:
        """
        Asserts that both the raw and hashed versions match, or don't match,
        according to ``self.should_match``.
        """
        log.info(
            f"Comparing:\n" f"- {self.person_a!r}\n" f"- {self.person_b!r}"
        )
        log.info("(1) Comparing plaintext")
        matches_raw, log_odds_plaintext = self.matches_plaintext()
        p_plaintext = probability_from_log_odds(log_odds_plaintext)
        p_plain_str = f"P(match | D) = {p_plaintext}"
        if matches_raw == self.should_match:
            if matches_raw:
                log.info(f"... should and does match: {p_plain_str}")
            else:
                log.info(f"... should not and does not match: {p_plain_str}")
        else:
            log_odds = log_odds_plaintext
            report = self.person_a.debug_comparison_report(
                self.person_b, verbose=False
            )
            raise AssertionError(
                f"Match failure: "
                f"matches_raw = {matches_raw}, "
                f"should_match = {self.should_match}, "
                f"log_odds = {log_odds}, "
                f"min_log_odds_for_match = {self.cfg.min_log_odds_for_match}, "
                f"P(match) = {probability_from_log_odds(log_odds)}, "
                f"person_a = {self.person_a}, "
                f"person_b = {self.person_b}, "
                f"report = {report}"
            )

        log.info(
            f"(2) Comparing hashed:\n"
            f"- {self.hashed_a}\n"
            f"- {self.hashed_b}"
        )
        matches_hashed, log_odds_hashed = self.matches_hashed()
        p_hashed = probability_from_log_odds(log_odds_hashed)
        p_hashed_str = f"P(match | D) = {p_hashed}"
        if matches_hashed == self.should_match:
            if matches_hashed:
                log.info(f"... should and does match: {p_hashed_str}")
            else:
                log.info(f"... should not and does not match: {p_hashed_str}")
        else:
            log_odds = log_odds_hashed
            report = self.hashed_a.debug_comparison_report(
                self.hashed_b, verbose=False
            )
            raise AssertionError(
                f"Match failure: "
                f"matches_hashed = {matches_hashed}, "
                f"should_match = {self.should_match}, "
                f"log_odds = {log_odds}, "
                f"threshold = {self.cfg.min_log_odds_for_match}, "
                f"min_log_odds_for_match = {self.cfg.min_log_odds_for_match}, "
                f"P(match) = {probability_from_log_odds(log_odds)}, "
                f"person_a = {self.person_a}, "
                f"person_b = {self.person_b}, "
                f"hashed_a = {self.hashed_a}, "
                f"hashed_b = {self.hashed_b}, "
                f"report = {report}"
            )

        log.info(
            "(3) Results of plaintext match should equal result of hashed "
            "match"
        )
        if log_odds_hashed != log_odds_plaintext:
            raise AssertionError(
                "Plaintext/hashed comparison discrepancy: "
                f"person_a = {self.person_a}, "
                f"person_b = {self.person_b}, "
                "log_odds_plaintext = {log_odds_plaintext}, "
                f"log_odds_hashed = {log_odds_hashed}"
            )


# =============================================================================
# Unit tests
# =============================================================================


class DummyTemporalIdentifierTests(unittest.TestCase):
    """
    Unit tests for :class:`DummyTemporalIdentifier`.
    """

    def test_overlap(self) -> None:
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 3)
        d4 = Date(2000, 1, 4)
        p = "dummypostcode"
        # ---------------------------------------------------------------------
        # Overlaps
        # ---------------------------------------------------------------------
        self.assertEqual(
            TemporalIDHolder(p, d1, d2).overlaps(TemporalIDHolder(p, d2, d3)),
            True,
        )
        self.assertEqual(
            TemporalIDHolder(p, d2, d3).overlaps(TemporalIDHolder(p, d1, d2)),
            True,
        )
        self.assertEqual(
            TemporalIDHolder(p, d1, d4).overlaps(TemporalIDHolder(p, d2, d3)),
            True,
        )
        self.assertEqual(
            TemporalIDHolder(p, d1, None).overlaps(
                TemporalIDHolder(p, None, d4)
            ),
            True,
        )
        self.assertEqual(
            TemporalIDHolder(p, None, None).overlaps(
                TemporalIDHolder(p, None, None)
            ),
            True,
        )
        # ---------------------------------------------------------------------
        # Non-overlaps
        # ---------------------------------------------------------------------
        self.assertEqual(
            TemporalIDHolder(p, d1, d2).overlaps(TemporalIDHolder(p, d3, d4)),
            False,
        )
        self.assertEqual(
            TemporalIDHolder(p, None, d1).overlaps(
                TemporalIDHolder(p, d2, None)
            ),
            False,
        )


class FuzzyLinkageTests(unittest.TestCase):
    """
    Tests of the fuzzy linkage system.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cfg = mk_test_config(rounding_sf=None)
        self.p1 = Postcode(
            cfg=self.cfg,
            postcode="CB2 0QQ",  # Addenbrooke's Hospital
            start_date=Date(2000, 1, 1),
            end_date=Date(2010, 1, 1),
        )
        self.p2 = Postcode(
            cfg=self.cfg,
            postcode="CB2 3EB",  # Department of Psychology
            start_date=Date(2000, 1, 1),
            end_date=Date(2010, 1, 1),
        )
        self.alice_bcd_rarename_2000_add = Person(
            cfg=self.cfg,
            local_id="1",
            forenames=["Alice", "Beatrice", "Celia", "Delilah"],
            surnames=["Rarename"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.alec_bcd_rarename_2000_add = Person(
            cfg=self.cfg,
            local_id="2",
            forenames=["Alec", "Beatrice", "Celia", "Delilah"],
            # Alec: same metaphone as Alice
            surnames=["Rarename"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.bob_bcd_rarename_2000_add = Person(
            cfg=self.cfg,
            local_id="3",
            forenames=["Bob", "Beatrice", "Celia", "Delilah"],
            surnames=["Rarename"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.alice_bc_rarename_2000_add = Person(
            cfg=self.cfg,
            local_id="4",
            forenames=["Alice", "Beatrice", "Celia"],
            surnames=["Rarename"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.alice_b_rarename_2000_add = Person(
            cfg=self.cfg,
            local_id="5",
            forenames=["Alice", "Beatrice"],
            surnames=["Rarename"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.alice_jones_2000_add = Person(
            cfg=self.cfg,
            local_id="6",
            forenames=["Alice"],
            surnames=["Jones"],
            dob="2000-01-01",
            postcodes=[self.p1],
        )
        self.bob_smith_1950_psych = Person(
            cfg=self.cfg,
            local_id="7",
            forenames=["Bob"],
            surnames=["Smith"],
            dob="1950-05-30",
            postcodes=[self.p2],
        )
        self.alice_smith_1930 = Person(
            cfg=self.cfg,
            local_id="8",
            forenames=["Alice"],
            surnames=["Smith"],
            dob="1930-01-01",
        )
        self.alice_smith_2000 = Person(
            cfg=self.cfg,
            local_id="9",
            forenames=["Alice"],
            surnames=["Smith"],
            dob="2000-01-01",
        )
        self.alice_smith = Person(
            cfg=self.cfg,
            local_id="10",
            forenames=["Alice"],
            surnames=["Smith"],
        )
        self.alice_bc_smith = Person(
            cfg=self.cfg,
            local_id="11",
            forenames=["Alice", "Betty", "Caroline"],
            surnames=["Smith"],
        )
        self.alice_bde_smith = Person(
            cfg=self.cfg,
            local_id="12",
            forenames=["Alice", "Betty", "Dorothy", "Elizabeth"],
            surnames=["Smith"],
        )
        self.all_people = [
            self.alice_bcd_rarename_2000_add,
            self.alec_bcd_rarename_2000_add,
            self.bob_bcd_rarename_2000_add,
            self.alice_bc_rarename_2000_add,
            self.alice_b_rarename_2000_add,
            self.alice_jones_2000_add,
            self.bob_smith_1950_psych,
            self.alice_smith_1930,
            self.alice_smith_2000,
            self.alice_smith,
            self.alice_bc_smith,
            self.alice_bde_smith,
        ]
        self.all_people_hashed = [p.hashed() for p in self.all_people]
        self.people_plaintext = People(cfg=self.cfg)
        self.people_plaintext.add_people(self.all_people)
        self.people_hashed = People(cfg=self.cfg)
        self.people_hashed.add_people(self.all_people_hashed)

    # -------------------------------------------------------------------------
    # Basic string transformations
    # -------------------------------------------------------------------------

    def test_standardize_name(self) -> None:
        tests = (
            # name, standardized version
            ("Al Jazeera", "ALJAZEERA"),
            ("Al'Jazeera", "ALJAZEERA"),
            ("Al'Jazeera'", "ALJAZEERA"),
            ("Alice", "ALICE"),
            ("ALJAZEERA", "ALJAZEERA"),
            ("aljazeera", "ALJAZEERA"),
            ("D'Souza", "DSOUZA"),
            ("de Clérambault", "DECLERAMBAULT"),
            ("Mary Ellen", "MARYELLEN"),
            ('"Al Jazeera"', "ALJAZEERA"),
            ("Müller", "MULLER"),
            ("Straße", "STRASSE"),
        )
        for item, target in tests:
            self.assertEqual(standardize_name(item), target)

    def test_safe_upper(self) -> None:
        tests = (
            ("Beethoven", "BEETHOVEN"),
            ("Clérambault", "CLÉRAMBAULT"),
            ("Straße", "STRAẞE"),
        )
        for a, b in tests:
            self.assertEqual(safe_upper(a), b)

    def test_remove_redundant_whitespace(self) -> None:
        tests = ((" van \t \r \n Beethoven ", "van Beethoven"),)
        for a, b in tests:
            self.assertEqual(remove_redundant_whitespace(a), b)

    def test_simplify_punctuation_whitespace(self) -> None:
        tests = (
            ("\n ‘John said “hello”.’", "  'John said \"hello\".'"),
            ("\t a–b—c−d-e ", "  a-b-c-d-e "),
        )
        for a, b in tests:
            self.assertEqual(simplify_punctuation_whitespace(a), b)

    def test_surname_fragments(self) -> None:
        cfg = self.cfg
        accent_transliterations = cfg.accent_transliterations
        nonspecific_name_components = cfg.nonspecific_name_components
        tests = (
            # In the expected answer, the original name (standardized) comes
            # first; then alphabetical order of all other variants. Some
            # examples are silly.
            #
            # France/French:
            (
                "Côte d'Ivoire",
                ["CÔTEDIVOIRE", "COTE", "COTEDIVOIRE", "CÔTE", "IVOIRE"],
            ),
            (
                "de Clérambault",
                [
                    "DECLÉRAMBAULT",
                    "CLERAMBAULT",
                    "CLÉRAMBAULT",
                    "DECLERAMBAULT",
                ],
            ),
            (
                "de la Billière",
                ["DELABILLIÈRE", "BILLIERE", "BILLIÈRE", "DELABILLIERE"],
            ),
            ("Façade", ["FAÇADE", "FACADE"]),
            ("Giscard d'Estaing", ["GISCARDDESTAING", "ESTAING", "GISCARD"]),
            ("L'Estrange", ["LESTRANGE", "ESTRANGE"]),
            ("L’Estrange", ["LESTRANGE", "ESTRANGE"]),
            # Germany (and in Beethoven's case, ancestrally Belgium):
            ("Beethoven", ["BEETHOVEN"]),
            ("Mozart Smith", ["MOZARTSMITH", "MOZART", "SMITH"]),
            ("Mozart-Smith", ["MOZARTSMITH", "MOZART", "SMITH"]),
            ("Müller", ["MÜLLER", "MUELLER", "MULLER"]),
            ("Straße", ["STRAẞE", "STRASSE"]),
            ("van  Beethoven", ["VANBEETHOVEN", "BEETHOVEN"]),
            # Italy:
            ("Calabrò", ["CALABRÒ", "CALABRO"]),
            ("De Marinis", ["DEMARINIS", "MARINIS"]),
            ("di Bisanzio", ["DIBISANZIO", "BISANZIO"]),
            # Sweden:
            ("Nyström", ["NYSTRÖM", "NYSTROEM", "NYSTROM"]),
            # Hmm. NYSTROEM is a German-style transliteration. Still, OK-ish.
        )
        for surname, target_fragments in tests:
            self.assertEqual(
                surname_alternative_fragments(
                    surname=surname,
                    accent_transliterations=accent_transliterations,
                    nonspecific_name_components=nonspecific_name_components,
                ),
                target_fragments,
            )

    def test_date_regex(self) -> None:
        for b in BAD_DATE_STRINGS:
            self.assertFalse(is_valid_isoformat_date(b))
        for g in GOOD_DATE_STRINGS:
            self.assertTrue(is_valid_isoformat_date(g))

    def test_standardize_postcode(self) -> None:
        tests = (
            # name, standardized version
            ("CB20QQ", "CB20QQ"),
            ("   CB2 0QQ   ", "CB20QQ"),
            ("   CB2-0 QQ   ", "CB20QQ"),
            ("cb2 0qq", "CB20QQ"),
        )
        for item, target in tests:
            self.assertEqual(standardize_postcode(item), target)

    def test_get_postcode_sector(self) -> None:
        tests = (
            # postcode, sector
            ("CB20QQ", "CB20"),
            ("   CB2 0QQ   ", "CB20"),
            ("   CB2-0 QQ   ", "CB20"),
            ("cb2 0qq", "CB20"),
        )
        for item, target in tests:
            self.assertEqual(get_postcode_sector(item), target)

    def test_postcode_regex(self) -> None:
        for b in BAD_POSTCODES:
            self.assertIsNone(
                POSTCODE_REGEX.match(b), f"Postcode {b!r} matched but is bad"
            )
            sb = standardize_postcode(b)
            self.assertIsNone(
                POSTCODE_REGEX.match(sb),
                f"Postcode {b!r} matched after standardization to {sb!r} "
                f"but is bad",
            )
        for g in GOOD_POSTCODES:
            sg = standardize_postcode(g)
            self.assertTrue(
                POSTCODE_REGEX.match(sg),
                f"Postcode {sg!r} (from {g!r}) did not match but is good",
            )

    # -------------------------------------------------------------------------
    # Frequencies
    # -------------------------------------------------------------------------

    def test_fuzzy_linkage_frequencies_name(self) -> None:
        cfg = self.cfg
        for surname in [
            "Smith",
            "Jones",
            "Blair",
            "Cardinal",
            "XYZ",
            "W",  # no metaphone
        ]:
            f = cfg.get_surname_freq_info(surname)
            log.info(f"Surname frequency for {surname}: {f}")

            self.assertIsInstance(f.name, str)
            self.assertIsInstance(f.gender, str)
            self.assertIsInstance(f.p_name, float)

            self.assertIsInstance(f.metaphone, str)
            self.assertIsInstance(f.p_metaphone, float)
            self.assertIsInstance(f.p_metaphone_not_name, float)

            self.assertIsInstance(f.f2c, str)
            self.assertIsInstance(f.p_f2c, float)
            self.assertIsInstance(f.p_f2c_not_name_metaphone, float)

        for forename, gender in [
            ("James", GENDER_MALE),
            ("Rachel", GENDER_FEMALE),
            ("Phoebe", GENDER_FEMALE),
            ("Elizabeth", GENDER_FEMALE),
            ("Elizabeth", GENDER_MALE),
            ("Elizabeth", ""),
            ("Rowan", GENDER_FEMALE),
            ("Rowan", GENDER_MALE),
            ("Rowan", ""),
            ("XYZ", ""),
            ("W", ""),  # no metaphone
        ]:
            f = cfg.get_forename_freq_info(forename, gender)
            log.info(
                f"Forename frequency for {forename}, gender {gender}: {f}"
            )
            self.assertIsInstance(f.name, str)
            self.assertIsInstance(f.gender, str)
            self.assertIsInstance(f.p_name, float)

            self.assertIsInstance(f.metaphone, str)
            self.assertIsInstance(f.p_metaphone, float)
            self.assertIsInstance(f.p_metaphone_not_name, float)

            self.assertIsInstance(f.f2c, str)
            self.assertIsInstance(f.p_f2c, float)
            self.assertIsInstance(f.p_f2c_not_name_metaphone, float)

    def test_fuzzy_linkage_frequencies_postcode(self) -> None:
        cfg = self.cfg
        # Examples are hospitals and colleges in Cambridge (not residential)
        # but it gives a broad idea.
        for postcode in ["CB2 0QQ", "CB2 0SZ", "CB2 3EB", "CB3 9DF"]:
            p = cfg.debug_postcode_unit_population(postcode)
            log.info(
                f"Calculated population for postcode unit {postcode}: {p}"
            )

        for ps in ["CB2 0", "CB2 1", "CB2 2", "CB2 3"]:
            p = cfg.debug_postcode_sector_population(ps)
            log.info(f"Calculated population for postcode sector {ps}: {p}")

    # -------------------------------------------------------------------------
    # Identifiers
    # -------------------------------------------------------------------------

    def test_identifier_dob(self) -> None:
        cfg = self.cfg

        for b in BAD_DATE_STRINGS:
            with self.assertRaises(ValueError):
                _ = DateOfBirth(cfg, b)

        full_match_log_lr = None  # type: Optional[float]
        for g in GOOD_DATE_STRINGS:
            d = DateOfBirth(cfg, g)
            self.assertEqual(d.dob_str, g)
            self.assertEqual(str(d), g)
            self.assertTrue(d.fully_matches(d))
            full_match_log_lr = d.comparison(d).posterior_log_odds(0)
            self.assertGreater(full_match_log_lr, 0)

        partial_matches = (
            ("2000-01-01", "2007-01-01"),  # year mismatch only
            ("2000-01-01", "2000-07-01"),  # month mismatch only
            ("2000-01-01", "2000-01-07"),  # day mismatch only
        )
        partial_match_log_lr = None  # type: Optional[float]
        for d1_str, d2_str in partial_matches:
            d1 = DateOfBirth(cfg, d1_str)
            d2 = DateOfBirth(cfg, d2_str)
            self.assertFalse(d1.fully_matches(d2))
            self.assertFalse(d2.fully_matches(d1))
            self.assertTrue(d1.partially_matches(d2))
            self.assertTrue(d2.partially_matches(d1))
            partial_match_log_lr = d1.comparison(d2).posterior_log_odds(0)
            self.assertLess(partial_match_log_lr, full_match_log_lr)

        not_partial_matches = (
            ("2000-01-01", "2007-07-01"),  # only day the same
            ("2000-01-01", "2000-07-07"),  # only year the same
            ("2000-01-01", "2007-01-07"),  # only month the same
        )
        for d1_str, d2_str in not_partial_matches:
            d1 = DateOfBirth(cfg, d1_str)
            d2 = DateOfBirth(cfg, d2_str)
            self.assertFalse(d1.fully_matches(d2))
            self.assertFalse(d2.fully_matches(d1))
            self.assertFalse(d1.partially_matches(d2))
            self.assertFalse(d2.partially_matches(d1))
            mismatch_log_lr = d1.comparison(d2).posterior_log_odds(0)
            self.assertLess(mismatch_log_lr, 0)
            self.assertLess(mismatch_log_lr, partial_match_log_lr)

    def test_identifier_postcode(self) -> None:
        cfg = self.cfg
        configs = [
            cfg,
            # Check extremes of k_postcode:
            mk_test_config(k_postcode=1),
            mk_test_config(k_postcode=1000),
            # Check extremes of p_unknown_or_pseudo_postcode, k_pseudopostcode:
            mk_test_config(
                p_unknown_or_pseudo_postcode=0.00001, k_pseudopostcode=1.2
            ),
            mk_test_config(
                p_unknown_or_pseudo_postcode=0.01, k_pseudopostcode=3
            ),
            # Very high combinations, e.g.
            # p_unknown_or_pseudo_postcode=0.00001, k_pseudopostcode=1.001, may
            # cause an error here. Very high combinations, e.g.
            # p_unknown_or_pseudo_postcode=0.1, k_pseudopostcode=3, may also
            # cause an error.
        ]
        # Any invalid settings are detected by the Postcode identifier class
        # checking that its comparisons are in a sensible order. All
        # identifiers do this, in fact.

        for b in BAD_POSTCODES:
            with self.assertRaises(ValueError):
                _ = Postcode(cfg, b)
        early = Date(2020, 1, 1)
        late = Date(2021, 12, 31)
        for g in GOOD_POSTCODES:  # includes pseudopostcodes
            with self.assertRaises(ValueError):
                _ = Postcode(cfg, g, start_date=late, end_date=early)
            p = Postcode(cfg, g)
            self.assertEqual(p.postcode_unit, standardize_postcode(g))
            self.assertTrue(p.fully_matches(p))

        empty = Postcode(cfg, "")
        self.assertEqual(str(empty), "")

        probe_partial_mismatch = (
            # Each tuple: (1) a postcode; (2) same sector, different unit; (3)
            # different sector.
            ("CB99 9XY", "CB99 9AB", "CB99 7AB"),  # nonsense
            ("CB2 0QQ", "CB2 0SL", "SW1A 2AA"),  # CUH 1, CUH 2, 10 Downing St
            ("ZZ99 3VZ", "ZZ99 3WZ", "ZZ99 1WZ"),  # pseudo: NFA, sea, Orkney
        )
        for probe_str, partial_str, mismatch_str in probe_partial_mismatch:
            for c in configs:
                p1 = Postcode(c, probe_str)
                p2 = Postcode(c, partial_str)
                p3 = Postcode(c, mismatch_str)

                # Everything matches itself.
                self.assertTrue(p1.fully_matches(p1))
                self.assertTrue(p2.fully_matches(p2))
                self.assertTrue(p3.fully_matches(p3))

                # Nothing matches another.
                self.assertFalse(p1.fully_matches(p2))
                self.assertFalse(p1.fully_matches(p3))
                self.assertFalse(p2.fully_matches(p3))

                # The partial match partially matches.
                self.assertTrue(p1.partially_matches(p2))

                # The nonmatch doesn't partially match.
                self.assertFalse(p1.partially_matches(p3))

                full_comp = p1.comparison(p1)
                full_log_lr = full_comp.posterior_log_odds(0)
                partial_comp = p1.comparison(p2)
                partial_log_lr = partial_comp.posterior_log_odds(0)
                nonmatch_comp = p1.comparison(p3)
                nonmatch_log_lr = nonmatch_comp.posterior_log_odds(0)

                self.assertGreater(
                    full_log_lr,
                    0,
                    f"comparing {probe_str!r} to itself, giving {full_comp!r}",
                )
                self.assertLess(
                    partial_log_lr,
                    full_log_lr,
                    f"comparing {probe_str!r} to {partial_str!r} "
                    f"(partial match); \ncfg = {cfg};\n"
                    f"p1 = {p1!r};\n"
                    f"giving {partial_comp!r}, versus the exact comparison "
                    f"{full_comp!r}",
                )
                self.assertLess(
                    nonmatch_log_lr,
                    partial_log_lr,
                    f"comparing {probe_str!r} to {mismatch_str!r} "
                    f"(nonmatch); \ncfg = {cfg};"
                    f"\np1 = {p1!r};\n"
                    f"giving {nonmatch_comp!r}, versus the previous partial "
                    f"comparison {partial_comp!r}",
                )

    def test_identifier_gender(self) -> None:
        cfg = self.cfg
        for b in BAD_GENDERS:
            with self.assertRaises(ValueError):
                _ = Gender(cfg, b)
        for g_str in VALID_GENDERS:
            g = Gender(cfg, g_str)
            log.critical(f"g = {g!r}")
            self.assertEqual(g.gender_str, g_str)
            self.assertEqual(str(g), g_str)
            if not g:
                continue
            self.assertTrue(g.fully_matches(g))
            comp = g.comparison(g)
            if comp:
                self.assertGreater(comp.posterior_log_odds(0), 0)

        empty = Gender(cfg, GENDER_MISSING)
        m = Gender(cfg, GENDER_MALE)
        f = Gender(cfg, GENDER_FEMALE)
        x = Gender(cfg, GENDER_OTHER)

        empty.ensure_has_freq_info_if_id_present()
        m.ensure_has_freq_info_if_id_present()
        f.ensure_has_freq_info_if_id_present()
        x.ensure_has_freq_info_if_id_present()

        self.assertEqual(str(empty), "")

        self.assertTrue(bool(m))
        self.assertTrue(bool(f))
        self.assertTrue(bool(x))
        self.assertFalse(bool(empty))

        self.assertTrue(m.fully_matches(m))
        self.assertTrue(m.comparison_relevant(m))

        self.assertTrue(f.comparison_relevant(f))
        self.assertTrue(f.comparison_relevant(f))

        self.assertFalse(m.fully_matches(f))
        self.assertFalse(m.fully_matches(x))
        self.assertFalse(f.fully_matches(m))
        self.assertFalse(f.fully_matches(x))

        f_comp_f = f.comparison(f)
        self.assertIsNotNone(f_comp_f)
        self.assertGreater(f.comparison(f).posterior_log_odds(0), 0)
        self.assertLess(f.comparison(m).posterior_log_odds(0), 0)

    def test_identifier_surname_fragment(self) -> None:
        cfg = self.cfg
        f1 = SurnameFragment(cfg, name="Smith", gender=GENDER_MALE)
        h1 = f1.hashed()
        self.assertTrue(f1.fully_matches(f1))
        self.assertTrue(f1.partially_matches(f1))
        self.assertFalse(f1.fully_matches(h1))
        self.assertFalse(f1.partially_matches(h1))
        self.assertTrue(h1.fully_matches(h1))
        self.assertTrue(h1.partially_matches(h1))

    def test_identifier_surname(self) -> None:
        # https://en.wikipedia.org/wiki/Double-barrelled_name
        cfg = self.cfg
        g = GENDER_FEMALE
        jones = Surname(cfg, name="Jones", gender=g)
        mozart = Surname(cfg, name="Mozart", gender=g)
        mozart_smith_hy = Surname(cfg, name="Mozart-Smith", gender=g)
        mozart_smith_sp = Surname(cfg, name="Mozart Smith", gender=g)
        smith = Surname(cfg, name="Smith", gender=g)
        smythe = Surname(cfg, name="Smythe", gender=g)
        mozart_hashed = mozart.hashed()
        mozart_smith_hashed = mozart_smith_hy.hashed()
        smith_hashed = smith.hashed()
        smythe_hashed = smythe.hashed()
        matching = [
            (jones, jones),
            (mozart_smith_hy, mozart),
            (mozart_smith_hy, mozart_smith_hy),
            (mozart_smith_hy, mozart_smith_sp),
            (mozart_smith_hy, smith),
            (mozart_smith_sp, mozart),
            (mozart_smith_sp, mozart_smith_hy),
            (mozart_smith_sp, smith),
            (smith, smith),
            (smythe, smythe),
            (mozart_hashed, mozart_hashed),
            (mozart_smith_hashed, mozart_smith_hashed),
            (smith_hashed, smith_hashed),
            (smythe_hashed, smythe_hashed),
        ]
        partially_matching = [
            (mozart_smith_hy, smythe),
            (mozart_smith_sp, smythe),
            (smith, smythe),
            (smith_hashed, smythe_hashed),
            (mozart_smith_hashed, smythe_hashed),
        ]
        nonmatching = [
            (jones, mozart_smith_hy),
            (jones, mozart_smith_sp),
            (smith, jones),
            (smith, mozart),
            (smith, smith_hashed),
            (smythe, smythe_hashed),
        ]
        for a, b in matching:
            self.assertTrue(a.fully_matches(b))
        for a, b in partially_matching:
            self.assertFalse(a.fully_matches(b))
            self.assertTrue(a.partially_matches(b))
        for a, b in nonmatching:
            self.assertFalse(a.fully_matches(b))
            self.assertFalse(a.partially_matches(b))

    # -------------------------------------------------------------------------
    # Lots of identifiers
    # -------------------------------------------------------------------------

    def test_identifier_transformations(self) -> None:
        """
        Creating hashed and plaintext JSON representation and loading an
        identifier back from them.
        """
        cfg = self.cfg
        identifiable = [
            DateOfBirth(cfg, dob="2000-12-31"),
            Forename(cfg, name="Elizabeth", gender=GENDER_FEMALE),
            Gender(cfg, gender=GENDER_MALE),
            PerfectID(cfg, identifiers={"nhsnum": 1}),
            Postcode(cfg, postcode="CB2 0QQ"),
            Surname(cfg, name="Smith", gender=GENDER_FEMALE),
            SurnameFragment(cfg, name="Smith", gender=GENDER_MALE),
        ]  # type: List[Identifier]
        for i in identifiable:
            self.assertTrue(i.is_plaintext)
            i_class = type(i)  # type: Type[Identifier]

            hd = i.as_dict(encrypt=True, include_frequencies=True)
            h = i_class.from_dict(cfg, hd, hashed=True)
            self.assertFalse(h.is_plaintext)
            h.ensure_has_freq_info_if_id_present()

            pd = i.as_dict(encrypt=False, include_frequencies=True)
            p = i_class.from_dict(cfg, pd, hashed=False)
            self.assertTrue(p.is_plaintext)
            p.ensure_has_freq_info_if_id_present()

    # -------------------------------------------------------------------------
    # Person checks
    # -------------------------------------------------------------------------

    def test_person_creation(self) -> None:
        cfg = self.cfg
        # Test the removal of blank names, etc.
        space = " "
        blank = ""
        p1 = Person(
            cfg, local_id="p1", forenames=["A", blank, space, None, "B"]
        )
        self.assertEqual(len(p1.forenames), 2)
        p2 = Person(
            cfg, local_id="p2", surnames=["A", blank, space, None, "B"]
        )
        self.assertEqual(len(p2.surnames), 2)
        p3 = Person(
            cfg,
            local_id="p3",
            postcodes=[GOOD_POSTCODES[0], blank, space, GOOD_POSTCODES[1]],
        )
        self.assertEqual(len(p3.postcodes), 2)

    def test_person_equality(self) -> None:
        cfg = self.cfg
        p1 = Person(cfg, local_id="hello")
        p2 = Person(cfg, local_id="world")
        p3 = Person(cfg, local_id="world")
        self.assertNotEqual(p1, p2)
        self.assertEqual(p2, p3)

        people = People(cfg)
        people.add_person(p1)
        people.add_person(p2)
        self.assertRaises(DuplicateIDError, people.add_person, p3)

    def test_person_copy(self) -> None:
        persons = [self.alice_smith]
        for orig in persons:
            cp = orig.copy()
            for attr in Person.ALL_PERSON_KEYS:
                orig_value = getattr(orig, attr)
                copy_value = getattr(cp, attr)
                self.assertEqual(
                    orig_value,
                    copy_value,
                    f"mismatch for {attr}:\n"
                    f"{orig_value!r}\n!=\n{copy_value!r}",
                )

    # -------------------------------------------------------------------------
    # Person comparisons
    # -------------------------------------------------------------------------

    def test_fuzzy_linkage_matches(self) -> None:
        test_values = [
            # Very easy match
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_bcd_rarename_2000_add,
                person_b=self.alice_bcd_rarename_2000_add,
                should_match=True,
            ),
            # Easy match
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_bc_rarename_2000_add,
                person_b=self.alice_b_rarename_2000_add,
                should_match=True,
            ),
            # Easy non-match
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_jones_2000_add,
                person_b=self.bob_smith_1950_psych,
                should_match=False,
            ),
            # Very ambiguous (1)
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_smith,
                person_b=self.alice_smith_1930,
                should_match=False,
            ),
            # Very ambiguous (2)
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_smith,
                person_b=self.alice_smith_2000,
                should_match=False,
            ),
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_bcd_rarename_2000_add,
                person_b=self.alec_bcd_rarename_2000_add,
                should_match=True,
            ),
            TestCondition(
                cfg=self.cfg,
                person_a=self.alice_bcd_rarename_2000_add,
                person_b=self.bob_bcd_rarename_2000_add,
                should_match=True,  # used to be False
            ),
        ]  # type: List[TestCondition]
        log.info("Testing comparisons...")
        for i, test in enumerate(test_values, start=1):
            log.info(f"Comparison {i}...")
            test.check_comparison_as_expected()

    def test_fuzzy_more_complex(self) -> None:
        log.info("Testing proband-versus-sample...")
        for i in range(len(self.all_people)):
            proband_plaintext = self.all_people[i]
            log.info(f"Plaintext search with proband: {proband_plaintext}")
            plaintext_winner = self.people_plaintext.get_unique_match(
                proband_plaintext
            )
            log.info(f"... WINNER: {plaintext_winner}")
            log.info(f"Hashed search with proband: {proband_plaintext}\n")
            proband_hashed = self.all_people_hashed[i]  # same order
            hashed_winner = self.people_hashed.get_unique_match(proband_hashed)
            log.info(f"... WINNER: {hashed_winner}")

    def test_exact_match(self) -> None:
        """
        Test the exact-match system.
        """
        id_type = "nhsnum"
        id_value = 3
        # Two people with no identifiers in common:
        p1 = Person(
            cfg=self.cfg, local_id="p1", perfect_id={id_type: id_value}
        )
        p2 = Person(
            cfg=self.cfg, local_id="p2", perfect_id={id_type: id_value}
        )
        # Perfect ID comparison is a function of a People object, not Person.
        people = People(cfg=self.cfg, people=[p1])

        # Match to self:
        result_p1 = people.get_unique_match_detailed(p1)
        self.assertEqual(result_p1.winner, p1)
        self.assertEqual(result_p1.best_log_odds, INFINITY)

        # Match to another with the same perfect ID:
        result_p2 = people.get_unique_match_detailed(p2)
        self.assertEqual(result_p2.winner, p1)
        self.assertEqual(result_p2.best_log_odds, INFINITY)

        # No two people in a People object with the same ID:
        self.assertRaises(DuplicateIDError, people.add_person, p2)

    # -------------------------------------------------------------------------
    # People checks
    # -------------------------------------------------------------------------
    # See also test_person_equality() above.

    def test_shortlist(self) -> None:
        """
        Our shortlisting process typically permits people with completely
        matching or partially matching DOBs, but not those with mismatched DOBs
        (for efficiency). Test that.
        """
        # Some test people:
        cfg1 = self.cfg
        proband = Person(cfg1, local_id="p1", dob="1950-01-01")
        full_dob_match = [
            # Full DOB match:
            Person(cfg1, local_id="p2", dob="1950-01-01"),
        ]
        partial_dob_match = [
            # Two components of DOB match:
            Person(cfg1, local_id="p3", dob="2000-01-01"),
            Person(cfg1, local_id="p4", dob="1950-12-01"),
            Person(cfg1, local_id="p5", dob="1950-01-12"),
        ]
        dob_mismatch = [
            # One component of DOB matches:
            Person(cfg1, local_id="p6", dob="1950-12-12"),
            Person(cfg1, local_id="p7", dob="2000-01-12"),
            Person(cfg1, local_id="p8", dob="2000-12-01"),
            # No component of DOB matches:
            Person(cfg1, local_id="p9", dob="2000-12-12"),
        ]
        all_people = (
            [proband] + full_dob_match + partial_dob_match + dob_mismatch
        )

        # A setup where we don't shortlist mismatched DOBs:
        self.assertEqual(cfg1.complete_dob_mismatch_allowed, False)
        self.assertEqual(cfg1.partial_dob_mismatch_allowed, True)
        people1 = People(cfg1, people=all_people)
        shortlist1 = list(people1.gen_shortlist(proband))
        self.assertTrue(proband in shortlist1)
        for full_p in full_dob_match:
            self.assertTrue(full_p in shortlist1)
        for partial_p in partial_dob_match:
            self.assertTrue(partial_p in shortlist1)
        for mismatch_p in dob_mismatch:
            self.assertFalse(mismatch_p in shortlist1)

        # And one where we do:
        cfg2 = mk_test_config(p_en_dob=FuzzyDefaults.P_EN_DOB_TRUE)
        self.assertEqual(cfg2.complete_dob_mismatch_allowed, True)
        self.assertEqual(cfg2.partial_dob_mismatch_allowed, True)
        people2 = People(cfg2, people=all_people)
        shortlist2 = list(people2.gen_shortlist(proband))
        for p in all_people:
            self.assertTrue(p in shortlist2)

        # And one where only exact DOB matches are allows:
        cfg3 = mk_test_config(p_ep_dob=0, p_en_dob=0)
        self.assertEqual(cfg3.complete_dob_mismatch_allowed, False)
        self.assertEqual(cfg3.partial_dob_mismatch_allowed, False)
        people3 = People(cfg3, people=all_people)
        shortlist3 = list(people3.gen_shortlist(proband))
        self.assertTrue(proband in shortlist3)
        for full_p in full_dob_match:
            self.assertTrue(full_p in shortlist3)
        for partial_p in partial_dob_match:
            self.assertFalse(partial_p in shortlist3)
        for mismatch_p in dob_mismatch:
            self.assertFalse(mismatch_p in shortlist3)


# -------------------------------------------------------------------------
# Multiple comparison correction checks
# -------------------------------------------------------------------------


class MultipleComparisonTestBase(unittest.TestCase):
    P_U = 0.1  # arbitrary
    P_O = 1 - P_U
    DELTA = 1e-10  # floating-point tolerance


class UnorderedMultipleComparisonTests(MultipleComparisonTestBase):
    @staticmethod
    def compare(
        proband_identifiers: List[Identifier],
        candidate_identifiers: List[Identifier],
    ) -> List[Comparison]:
        return list(
            gen_best_comparisons(
                proband_identifiers=proband_identifiers,
                candidate_identifiers=candidate_identifiers,
                ordered=False,
            )
        )

    def test_same_single_id_returns_one_match_and_no_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # UNORDERED, one/one identifier
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")

        result = self.compare([a], [a])
        self.assertEqual(len(result), 1)  # ... one match, no correction

        comparison = result[0]
        self.assertIsInstance(comparison, DirectComparison)
        self.assertEqual(comparison.d_description, "dummy_match:A")

    def test_same_two_ids_returns_two_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Unordered, two/two identifiers
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")

        result = self.compare([a, b], [a, b])
        self.assertEqual(len(result), 3)  # ... two matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:B")
        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # Correction should be for 2 hits from 2 comparisons, and a Bonferroni
        # correction:
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, -ln(2), delta=self.DELTA
        )

    def test_same_three_ids_returns_three_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Unordered, three/three identifiers
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")
        c = DummyLetterIdentifier("C")

        result = self.compare([a, b, c], [a, b, c])
        self.assertEqual(len(result), 4)  # ... three matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:B")
        comparison3 = result[2]
        self.assertIsInstance(comparison3, DirectComparison)
        self.assertEqual(comparison3.d_description, "dummy_match:C")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # Correction should be for 3 hits from 6 comparisons:
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, -ln(6), delta=self.DELTA
        )

    def test_one_out_of_three_ids_returns_three_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Unordered, one/three identifiers
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")
        c = DummyLetterIdentifier("C")

        result = self.compare([a], [a, b, c])
        self.assertEqual(len(result), 2)  # ... one match and a correction

        comparison = result[0]
        self.assertIsInstance(comparison, DirectComparison)
        self.assertEqual(comparison.d_description, "dummy_match:A")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # Correction should be for 1 hit from 3 comparisons:
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, -ln(3), delta=self.DELTA
        )

    def test_with_incomparable_identifiers(self) -> None:
        """
        Use identifiers that aren't allowed to be compared, e.g. names with
        non-overlapping timestamps. This will give a comparison that is
        ``None``, and make the code coverage checks happy.

        .. code-block:: bash

            pip install pytest-cov
            pytest --cov --cov-report html
        """
        a_early = DummyLetterTemporalIdentifier(
            value="A", start_date="1900-01-01", end_date="1900-12-31"
        )
        a_late = DummyLetterTemporalIdentifier(
            value="A", start_date="2000-01-01", end_date="2000-12-31"
        )
        result = self.compare([a_early], [a_late])
        self.assertEqual(len(result), 0)  # no comparisons


class OrderedMultipleComparisonTests(MultipleComparisonTestBase):
    def compare(
        self,
        proband_identifiers: List[Identifier],
        candidate_identifiers: List[Identifier],
    ) -> List[Comparison]:
        return list(
            gen_best_comparisons(
                proband_identifiers=proband_identifiers,
                candidate_identifiers=candidate_identifiers,
                ordered=True,
                p_u=self.P_U,
            )
        )

    def test_same_single_identifier_returns_one_match_and_no_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ORDERED, one/one identifier
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")

        result = self.compare([a], [a])
        self.assertEqual(len(result), 1)  # ... one match, no correction

        comparison = result[0]
        self.assertIsInstance(comparison, DirectComparison)
        self.assertEqual(comparison.d_description, "dummy_match:A")

    def test_same_two_ids_same_order_returns_two_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Ordered, two/two identifiers, correct order
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")

        result = self.compare([a, b], [a, b])
        self.assertEqual(len(result), 3)  # ... two matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:B")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # - P(D|H) correction: +ln(p_o).
        # - P(D|¬H) correction: nothing, i.e. -ln(1) = 0.
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, ln(self.P_O), delta=self.DELTA
        )

    def test_same_two_ids_diff_order_returns_two_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Ordered, two/two identifiers, wrong order
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")

        result = self.compare([a, b], [b, a])
        self.assertEqual(len(result), 3)  # ... two matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:B")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # - P(D|H) correction: +ln(p_u).
        # - P(D|¬H) correction: Bonferroni for 2 options but minus one for the
        #   ordered option, so nothing.
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, ln(self.P_U), delta=self.DELTA
        )

    def test_same_three_ids_same_order_returns_three_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Ordered, three/three identifiers, correct order
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")
        c = DummyLetterIdentifier("C")

        result = self.compare([a, b, c], [a, b, c])
        self.assertEqual(len(result), 4)  # ... three matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:B")
        comparison3 = result[2]
        self.assertIsInstance(comparison3, DirectComparison)
        self.assertEqual(comparison3.d_description, "dummy_match:C")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # - P(D|H) correction: +ln(p_o).
        # - P(D|¬H) correction: nothing (correct order).
        self.assertAlmostEqual(
            correction.log_likelihood_ratio, ln(self.P_O), delta=self.DELTA
        )

    def test_same_three_ids_diff_order_returns_three_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Ordered, three/three identifiers, wrong order
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")
        c = DummyLetterIdentifier("C")

        result = self.compare([a, b, c], [b, c, a])
        self.assertEqual(len(result), 4)  # ... three matches and a correction

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:B")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:C")
        comparison3 = result[2]
        self.assertIsInstance(comparison3, DirectComparison)
        self.assertEqual(comparison3.d_description, "dummy_match:A")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # - P(D|H) correction: +ln(p_u).
        # - P(D|¬H) correction: Bonferroni for 6 options minus the one for the
        #   correct order.
        self.assertAlmostEqual(
            correction.log_likelihood_ratio,
            ln(self.P_U) - ln(5),
            delta=self.DELTA,
        )

    def test_two_of_three_matching_ids_returns_three_matches_and_a_correction(
        self,
    ) -> None:
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Ordered, three/three identifiers, two match, wrong order
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")
        c = DummyLetterIdentifier("C")
        d = DummyLetterIdentifier("D")

        """
        Comparing proband [a, b, c] to candidate [b, c, d]:

        p = proband index
        c = candidate index
        d = distance
        LLR = log likelihood ratio

                           p c d  LLR
        a - b  mismatch A  0 0 0  -4.5
        a - c  mismatch A  0 1 1  -4.5
        a - d  mismatch A  0 2 4  -4.5
        b - b  match B     1 0 1  3.2
        b - c  mismatch B  1 1 0  -4.5
        b - d  mismatch B  1 2 1  -4.5
        c - b  mismatch C  2 0 4  -4.5
        c - c  match C     2 1 1  3.2
        c - d  mismatch C  2 2 0  -4.5

        then we sort them by -LLR and distance:

                                        returned?
        b - b  match B     1 0 1  3.2   Yes
        c - c  match C     2 1 1  3.2   Yes
        a - b  mismatch A  0 0 0  -4.5  No (c=0 used)
        b - c  mismatch B  1 1 0  -4.5  No (p=1 or c=1 used)
        c - d  mismatch C  2 2 0  -4.5  No (p=2 used)
        a - c  mismatch A  0 1 1  -4.5  No (c=1 used)
        b - d  mismatch B  1 2 1  -4.5  No (p=1 used)
        a - d  mismatch A  0 2 4  -4.5  Yes
        c - b  mismatch C  2 0 4  -4.5  No (p=2 or c=0 used)

        """

        result = self.compare([a, b, c], [b, c, d])
        # ... three matches (but one will be bad) and a correction
        self.assertEqual(len(result), 4)

        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:B")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:C")
        comparison3 = result[2]
        self.assertIsInstance(comparison3, DirectComparison)
        self.assertEqual(comparison3.d_description, "dummy_mismatch:A")

        correction = result[-1]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        # - P(D|H) correction: +ln(p_u).
        # - P(D|¬H) correction: Bonferroni for 6 options minus the one for the
        #   correct order.
        self.assertAlmostEqual(
            correction.log_likelihood_ratio,
            ln(self.P_U) - ln(5),
            delta=self.DELTA,
        )

    def test_order_correct_with_duplicate_names_1(self) -> None:
        """
        Compare "A A" to "A A" in ordered fashion.

        Think of this as proband A_P1, A_P2 and candidate A_C1, A_C2.

        Should give a "correctly ordered" match, A_P1:A_C1 and A_C2:A_C2, with
        correction for P_O.

        Should not treat it as an incorrectly ordered match, A_P1:A_C2 and
        A_P2:A_C1, and apply a different correction for P_U etc.

        This might work without the "distance" sort in ComparisonInfo (it does,
        in fact), but that is a safety. See below for a test that does depend
        on that distance metric.
        """
        a = DummyLetterIdentifier("A")

        result = self.compare([a, a], [a, a])
        self.assertEqual(len(result), 3)
        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:A")
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_match:A")
        correction = result[2]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        self.assertAlmostEqual(
            correction.log_likelihood_ratio,
            ln(self.P_O),
            delta=self.DELTA,
        )

    def test_order_correct_with_duplicate_names_2(self) -> None:
        """
        Compare "A B" to "B B" in ordered fashion.

        We want this to give A_P1:B_P1 (mismatch) and B_P2:B_C2 (ordered
        match).

        It should not give A_P1:B_P2 (mismatch) and B_P2:B_C1 (unordered
        match).

        This does not work without the "distance" part of the sort in
        ComparisonInfo.
        """
        a = DummyLetterIdentifier("A")
        b = DummyLetterIdentifier("B")

        result = self.compare([a, b], [b, b])
        self.assertEqual(len(result), 3)
        # Matches come first (better LLR):
        comparison1 = result[0]
        self.assertIsInstance(comparison1, DirectComparison)
        self.assertEqual(comparison1.d_description, "dummy_match:B")
        # Then mismatches:
        comparison2 = result[1]
        self.assertIsInstance(comparison2, DirectComparison)
        self.assertEqual(comparison2.d_description, "dummy_mismatch:A")
        # Then corrections:
        correction = result[2]
        self.assertIsInstance(correction, AdjustLogOddsComparison)
        self.assertAlmostEqual(
            correction.log_likelihood_ratio,
            ln(self.P_O),
            delta=self.DELTA,
        )
