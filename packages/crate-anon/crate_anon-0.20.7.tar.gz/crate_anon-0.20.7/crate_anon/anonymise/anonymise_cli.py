#!/usr/bin/env python

"""
crate_anon/anonymise/anonymise_cli.py

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

**Command-line entry point for anonymisation.**

Split from the anonymisation functions so we can respond quickly to
command-line input; uses a delayed import when starting anonymisation.

"""

# Uses a delayed import (see below), so we can set up logging before
# using the config object.
import argparse
import logging
import os
from typing import List

from cardinal_pythonlib.logs import configure_logger_for_colour
from rich_argparse import ArgumentDefaultsRichHelpFormatter

from crate_anon.anonymise.constants import (
    ANON_CONFIG_ENV_VAR,
    DEFAULT_CHUNKSIZE,
    DEFAULT_REPORT_EVERY,
)
from crate_anon.common.exceptions import call_main_with_exception_reporting
from crate_anon.version import CRATE_VERSION_PRETTY

log = logging.getLogger(__name__)

DEBUG_RUN_WITH_PDB = False

if DEBUG_RUN_WITH_PDB:
    from cardinal_pythonlib.debugging import pdb_run
else:
    pdb_run = None


# =============================================================================
# Main
# =============================================================================


def inner_main() -> None:
    """
    Indirect command-line entry point. See command-line help.

    Calls :func:`crate_anon.anonymise.anonymise.anonymise`.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description=f"Database anonymiser. ({CRATE_VERSION_PRETTY})",
        formatter_class=ArgumentDefaultsRichHelpFormatter,
    )

    parser.add_argument(
        "--config",
        help=f"Config file (overriding environment variable "
        f"{ANON_CONFIG_ENV_VAR}).",
    )
    parser.add_argument(
        "--version", action="version", version=CRATE_VERSION_PRETTY
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Be verbose"
    )

    mode_options = parser.add_argument_group("Mode options")
    mode_group = mode_options.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-i",
        "--incremental",
        dest="incremental",
        action="store_true",
        help="Process only new/changed information, where possible.",
        default=True,
    )
    mode_group.add_argument(
        "-f",
        "--full",
        dest="incremental",
        action="store_false",
        help="Drop and remake everything.",
        default=False,
    )
    mode_options.add_argument(
        "--skipdelete",
        dest="skipdelete",
        action="store_true",
        help="For incremental updates, skip deletion of rows present in the "
        "destination but not the source.",
    )

    action_options = parser.add_argument_group(
        "Action options (default is to do all, but if any are specified, "
        "only those are done)"
    )
    action_options.add_argument(
        "--dropremake",
        action="store_true",
        help="Drop/remake destination tables, and admin tables except "
        "opt-out tables.",
    )
    action_options.add_argument(
        "--drop_all",
        action="store_true",
        help="Drop all destination tables known to the data dictionary, and "
        "all admin tables, then stop. (May also be helpful in revealing "
        "leftover tables in the destination database, e.g. if the data "
        "dictionary has changed.)",
    )
    action_options.add_argument(
        "--optout",
        action="store_true",
        help="Update opt-out list in administrative database.",
    )
    action_options.add_argument(
        "--nonpatienttables",
        action="store_true",
        help="Process non-patient tables only.",
    )
    action_options.add_argument(
        "--patienttables",
        action="store_true",
        help="Process patient tables only.",
    )
    action_options.add_argument(
        "--index", action="store_true", help="Create indexes only."
    )

    restrict_options = parser.add_argument_group("Restriction options")
    restrict_options.add_argument(
        "--restrict",
        help="Restrict which patients are processed. Specify which field to "
        "base the restriction on or 'pid' for patient ids.",
    )
    restrict_options.add_argument(
        "--limits",
        nargs=2,
        help="Specify lower and upper limits of the field "
        "specified in '--restrict'.",
    )
    restrict_options.add_argument(
        "--file",
        help="Specify a file with a list of values for the field "
        "specified in '--restrict'.",
    )
    restrict_options.add_argument(
        "--list",
        nargs="+",
        help="Specify a list of values for the field "
        "specified in '--restrict'.",
    )
    restrict_options.add_argument(
        "--free_text_limit",
        type=int,
        help="Filter out all free text fields over the specified length. "
        "For example, if you specify 200, then VARCHAR(200) fields will "
        "be permitted, but VARCHAR(200), or VARCHAR(MAX), or TEXT "
        "(etc., etc.) fields will be excluded.",
    )
    restrict_options.add_argument(
        "--excludescrubbed",
        action="store_true",
        help="Exclude all text fields which are being scrubbed.",
    )

    processing_options = parser.add_argument_group("Processing options")
    processing_options.add_argument(
        "--process",
        nargs="?",
        type=int,
        default=0,
        help="For multiprocess mode: specify process number.",
    )
    processing_options.add_argument(
        "--nprocesses",
        nargs="?",
        type=int,
        default=1,
        help="For multiprocess mode: specify total number of processes "
        "(launched somehow, of which this is to be one).",
    )
    processing_options.add_argument(
        "--processcluster",
        default="",
        help="Process cluster name (used as part of log name).",
    )
    processing_options.add_argument(
        "--skip_dd_check",
        action="store_true",
        help="Skip data dictionary validity check.",
    )
    processing_options.add_argument(
        "--seed",
        help="String to use as the basis of the seed for the random number "
        "generator used for the transient integer RID (TRID). Leave "
        "blank to use the default seed (system time).",
    )
    processing_options.add_argument(
        "--chunksize",
        nargs="?",
        type=int,
        default=DEFAULT_CHUNKSIZE,
        help="Number of records copied in a chunk when copying PKs from one "
        "database to another.",
    )

    debugging_options = parser.add_argument_group("Reporting and debugging")
    debugging_options.add_argument(
        "--reportevery",
        nargs="?",
        type=int,
        default=DEFAULT_REPORT_EVERY,
        help="Report insert progress every n rows in verbose mode.",
    )
    debugging_options.add_argument(
        "--debugscrubbers",
        action="store_true",
        help="Report sensitive scrubbing information, for debugging.",
    )
    debugging_options.add_argument(
        "--savescrubbers",
        action="store_true",
        help="Saves sensitive scrubbing information in admin database, "
        "for debugging.",
    )
    debugging_options.add_argument(
        "--echo", action="store_true", help="Echo SQL."
    )

    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Verbosity, logging
    # -------------------------------------------------------------------------

    mynames = []  # type: List[str]
    if args.processcluster:
        mynames.append(args.processcluster)
    if args.nprocesses > 1:
        mynames.append(f"proc{args.process}")
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    rootlogger = logging.getLogger()
    configure_logger_for_colour(rootlogger, loglevel, extranames=mynames)

    # -------------------------------------------------------------------------
    # Onwards
    # -------------------------------------------------------------------------

    if args.config:
        os.environ[ANON_CONFIG_ENV_VAR] = args.config

    # Delayed import; pass everything else on
    from crate_anon.anonymise.anonymise import anonymise  # delayed import

    anonymise(
        incremental=args.incremental,
        skipdelete=args.skipdelete,
        dropremake=args.dropremake,
        full_drop_only=args.drop_all,
        optout=args.optout,
        patienttables=args.patienttables,
        nonpatienttables=args.nonpatienttables,
        index=args.index,
        restrict=args.restrict,
        restrict_file=args.file,
        restrict_limits=args.limits,
        restrict_list=args.list,
        free_text_limit=args.free_text_limit,
        exclude_scrubbed_fields=args.excludescrubbed,
        nprocesses=args.nprocesses,
        process=args.process,
        skip_dd_check=args.skip_dd_check,
        seed=args.seed,
        chunksize=args.chunksize,
        reportevery=args.reportevery,
        echo=args.echo,
        debugscrubbers=args.debugscrubbers,
        savescrubbers=args.savescrubbers,
    )


def main() -> None:
    """
    Command-line entry point.
    """
    call_main_with_exception_reporting(inner_main)


# =============================================================================
# Command-line entry point
# =============================================================================

if __name__ == "__main__":
    if DEBUG_RUN_WITH_PDB:
        pdb_run(main)
    else:
        main()
