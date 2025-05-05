"""
crate_anon/ancillary/timely_project/timely_filter_systmone.py

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

Helper code for MRC TIMELY project (Moore, grant MR/T046430/1). Not of general
interest.

Information to filter SystmOne data dictionaries for TIMELY.

"""

# =============================================================================
# Imports
# =============================================================================

from typing import Optional, List, Tuple

from crate_anon.ancillary.timely_project.dd_criteria import (
    add_field_criteria,
    add_table_criteria,
    FieldCriterion,
    TableCriterion,
)
from crate_anon.ancillary.timely_project.timely_filter import TimelyDDFilter
from crate_anon.preprocess.systmone_ddgen import (
    SystmOneContext,
    TABLE_PREFIXES,
)


# =============================================================================
# TimelyCPFTRiOFilter
# =============================================================================


class TimelySystmOneFilter(TimelyDDFilter):
    """
    Filter a SystmOne data dictionary (with some CPFT extensions).
    """

    CONTEXT = SystmOneContext.TPP_SRE  # default context

    @classmethod
    def _add_tables(
        cls,
        criteria: List[TableCriterion],
        stage: Optional[int],
        regex_strings: List[str],
    ) -> None:
        """
        Apply a context-specific table prefix before adding table criteria.
        """
        table_prefix = TABLE_PREFIXES[cls.CONTEXT]
        prefixed_regex_strings = [table_prefix + t for t in regex_strings]
        add_table_criteria(criteria, stage, prefixed_regex_strings)

    @classmethod
    def _add_fields(
        cls,
        criteria: List[FieldCriterion],
        stage: Optional[int],
        regex_tuples: List[Tuple[str, str]],
    ) -> None:
        """
        Apply a context-specific table prefix before adding field criteria.
        """
        table_prefix = TABLE_PREFIXES[cls.CONTEXT]
        prefixed_regex_tuples = [
            (table_prefix + t, f) for t, f in regex_tuples
        ]
        add_field_criteria(criteria, stage, prefixed_regex_tuples)

    def __init__(self) -> None:
        super().__init__()

        # ---------------------------------------------------------------------
        # Generic exclusions
        # ---------------------------------------------------------------------

        self._add_tables(self.exclude_tables, stage=None, regex_strings=[])

        # ---------------------------------------------------------------------
        # Stage 1: demographics, problem lists, diagnoses, safeguarding,
        # contacts (e.g. referrals, contacts, discharge)
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=1,
            regex_strings=[
                "18WeekWait",  # referral info
                "Accommodation",  # e.g. lives in sheltered accommodation
                "ActivityEvent.*",  # e.g. attendance/non-attendance at appts
                "Appointments",  # contacts
                "CarerStatus",  # e.g. "is a carer"
                "Child_At_Risk",  # safeguarding
                "Child_Protection_Plan_Reason",  # safeguarding
                "Contacts.*",
                "CPA$",  # start date etc.
                "Deaths",
                "Demographics",
                "Diagnosis",
                "Disability.*",
                "Employment",
                "Event",  # nature of contact, e.g. face-to-face or e-mail
                "InpatientWardStay",
                "Medical_History_Previous_Diagnosis",
                "NDOptOutPreference",
                "Newborn_Bloodspot_.*",
                "OutOfHours.*",  # e.g. MIU contacts, dispositions
                "OverseasVisitorChargingCategory",  # demographics
                "Patient$",  # demographics
                "PatientAddress",  # demographics
                "PatientContact",  # useless?
                "PatientEthnicity",
                "PatientGPPractice",
                "PatientLanguageDeathOptions",  # language = demographics
                "PatientRelationship",  # e.g. "other is a carer for patient"
                "PatientSRCodeInformation",  # Read codes (e.g. diagnoses)
                "PersonAtRisk",  # safeguarding
                "PRISM_ReReferral",  # primary care MH service
                "Provisional_Diagnosis",  # diagnoses
                "ReferralAllocation$",  # teams
                "ReferralInReferralReason",  # picklist reason for referral
                "ReferralsIn",
                "ReferralsOut",
                "RiskReview",  # safeguarding
                "Safeguarding.*",
                "Secondary_Diagnosis",
                "SettledAccommodationIndicator",
                "SpecialEducationalNeeds",
                "Team",  # non-patient lookup table
                "TeamMember",  # non-patient lookup table
                "Templates",  # CTV3/SNOMED codes from templates
                "Vanguard",  # referrals to CPFT Vanguard MH service
                "WaitingList",  # contains some free text notes; see below
                "WaitList_EatingDisorders",  # referral waiting lists
                "WorkingHours",  # number of hours worked by patient
                # Views:
                "vsS1_OutOfHours",  # see OutOfHours above
                "vsS1_PatientAddressWithResearchGeography",
            ],
        )

        # ---------------------------------------------------------------------
        # Stage 2: detailed information about all service contacts, including
        # professional types involved, procedures, outcome data, etc.
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=2,
            regex_strings=[
                "AQ_.*",  # (fact of) answerered questionnaire
                "Clustering",  # care cluster classification
                "Coded_Procedure",
                "ECT.*",
                "EuroQol.*",  # quality-of-life outcome data
                "Goal",
                "NewbornHearingAudiologyOutcome",
                "NewbornHearingScreeningOutcome",
                "PhysicalHealthChecks",  # the fact of it being done
                "ReferralInIntervention",  # e.g. discharged, got better
                "SessionNotes_CTV3Code",  # who does what (in outline)
                "SessionNotes_Template",  # who does what (in outline)
                "Visit",  # home visits
                "WardAttender",
            ],
        )

        # ---------------------------------------------------------------------
        # Stage 3: prescribing data
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=3,
            regex_strings=[
                "CYPHS_502_Immunisation",
                "Immunisation",
            ],
        )

        # ---------------------------------------------------------------------
        # Stage 4: test results, other health assessments, other clinical info
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=4,
            regex_strings=[
                # fact of questionnaires being answered
                "AnsweredQuestionnaire",
                "AssistiveTechnologyToSupportDisability",
                "ClinicalMeasure_.*",
                "ClinicalOutcome_.*",
                "Coded_.*",  # finding, observations, [procedures: see 2], scored assessments  # noqa: E501
                "Falls_AtRiskState.*",
                "Inpatient_NorthwickParkIndex",  # may be current inpatients only  # noqa: E501
                "InpatientLeave",
                "MentalHealthAct.*",
                "PatientAnsweredQuestionnaireInformation",
                "PatientLetterInformation",
            ],
        )

        # ---------------------------------------------------------------------
        # Stage 5: (structured) info on care plans etc.
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=5,
            regex_strings=[
                "CarePlan.*",
                "CPA.*",  # the rest, except "CPA" above
                "RestrictiveIntervention",  # restrictive physical intervention
            ],
        )

        # ---------------------------------------------------------------------
        # Stage 6: de-identified free text
        # ---------------------------------------------------------------------

        self._add_tables(
            self.staged_include_tables,
            stage=6,
            regex_strings=[
                "CYPFRS_TelephoneTriage",
                "FreeText",
                "LADSCYPHS_Output",
                "LADSCYPQuestionnaires",
            ],
        )

        # ---------------------------------------------------------------------
        # Specific fields
        # ---------------------------------------------------------------------
        # Specific fields to exclude that would otherwise be included.
        # List of (tablename, fieldname) regex string tuples.

        self._add_fields(
            self.staged_exclude_fields,
            stage=5,
            regex_tuples=[
                # "exclude at stage 5 or earlier"
                ("WaitingList", "Notes")
            ],
        )


class TimelyCPFTGenericSystmOneFilter(TimelySystmOneFilter):
    """
    Whatever we would have got from TimelySystmOneFilter, but with table
    prefixes appropriate to the CPFT Data Warehouse.
    """

    CONTEXT = SystmOneContext.CPFT_DW
