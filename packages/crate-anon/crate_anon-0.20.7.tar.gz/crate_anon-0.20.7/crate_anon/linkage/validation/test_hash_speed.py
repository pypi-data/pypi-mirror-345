#!/usr/bin/env python

"""
crate_anon/linkage/validation/test_hash_speed.py

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

**Test the speed of hashing.**

The question is: if someone malicious learned a secret hash key, how long would
it take them to generate a reverse map from a known identifier space?

The test uses a single CPU core.

Specimen results, for padding length 9 and the HMAC_MD5 algorithm, on Wombat
(3.5 GHz CPU), tested with 100000 (1e5) iterations (which took 0.72 s, piping
to ``/dev/null``):

- 1e9 operations will take about 7200 s = 2 hours.
  This is the right order of magniture for NHS numbers (9 digits plus a
  checksum; other rules might restrict that a bit more).

- 7.3e12 operations will take about 52667022 s = 1.7 years
  This is the right order of magnitude for NHS numbers plus dates of birth
  covering 20 years (1e9 for NHS number * 365 days/year * 20 years).

- 3.65e13 operations will take about 263335113 s = 8.4 years
  This is the right order of magnitude for NHS numbers plus DOBs covering
  a century (1e9 for NHS number * 365 days/year * 100 years).

The hash algorithm isn't a major factor; moving from HMAC_MD5 to HMAC_SHA512,
for example, only takes the time for 1e5 iterations from 0.72 s to 0.86 s.

(A subsequent test: faster, at 5443 s = 1.5 h, 1.25 y, and 6.3 y respectively.)

Speed tests considered for paper (not used in the end; real-world measures
used):

.. code-block:: bash

    ./test_hash_speed.py --method HMAC_MD5 --ntests 1000000 > /dev/null
    ./test_hash_speed.py --method HMAC_SHA256 --ntests 1000000 > /dev/null
    ./test_hash_speed.py --method HMAC_SHA512 --ntests 1000000 > /dev/null

"""

import argparse
import logging
import time
from typing import Iterable, List, TextIO

from cardinal_pythonlib.file_io import smart_open, writeline_nl
from cardinal_pythonlib.logs import main_only_quicksetup_rootlogger
from cardinal_pythonlib.hash import HashMethods, make_hasher
from cardinal_pythonlib.randomness import generate_random_string
from rich_argparse import ArgumentDefaultsRichHelpFormatter

log = logging.getLogger(__name__)


def gen_dummy_data(n: int, string_length: int) -> Iterable[str]:
    """
    Generate some random strings of the specified width
    """
    for i in range(n):
        yield str(n).ljust(string_length, "x")


def test_hash_speed(
    output_filename: str,
    hash_method: str,
    key: str,
    ntests: int,
    intended_possibilities: List[int],
    string_length: int,
):
    """
    Hash lines from one file to another.

    Args:
        output_filename:
            Output filename, or "-" for stdin
        hash_method:
            Method to use; e.g. ``HMAC_SHA256``
        key:
            Secret key for hasher
        ntests:
            Number of hashes to perform.
        intended_possibilities:
            Number of hashes to estimate time for.
        string_length:
            Length of each string to hash (characters).

    Note that the hash precedes the ID with the ``keep_id`` option, which
    works best if the ID might contain commas.
    """
    log.info(f"Writing to: {output_filename}")
    log.info(f"Using hash method: {hash_method}")
    log.info(f"Hashing some random data {ntests} times, using one CPU core")
    log.info(f"String length: {string_length}")
    log.debug(f"Using key: {key!r}")  # NB security warning in help

    hasher = make_hasher(hash_method=hash_method, key=key)
    with smart_open(output_filename, "wt") as o:  # type: TextIO
        start_time = time.time()
        for data in gen_dummy_data(ntests, string_length):
            hashed = hasher.hash(data)
            writeline_nl(o, f"{data} -> {hashed}")
        end_time = time.time()

    time_taken_s = end_time - start_time
    log.info(f"Start time (s): {start_time}")
    log.info(f"End time (s): {end_time}")
    log.info(f"Time taken (s): {time_taken_s}")
    log.info(f"Number of hash operations: {ntests}")
    log.info(f"Hash operations per second: {ntests / time_taken_s}")
    for intended in intended_possibilities:
        estimated_time_s = intended * time_taken_s / ntests
        log.info(
            f"For {intended} operations (on a single CPU core), "
            f"estimated time (s): {estimated_time_s}"
        )


def main() -> None:
    """
    Command-line entry point.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description="Test the speed of a hash method.",
        formatter_class=ArgumentDefaultsRichHelpFormatter,
    )
    parser.add_argument(
        "--outfile",
        type=str,
        default="-",
        help="Output file; can use '-' for stdout (and redirect to "
        "/dev/null, which you should do for 'core' speed testing).",
    )
    parser.add_argument(
        "--key",
        type=str,
        help="Key for hasher. Ordinarily this would be secret, but this is "
        "just for testing. Default is random.",
    )
    parser.add_argument(
        "--keyfile",
        type=str,
        help="File whose first noncomment line contains the secret key for "
        "the hasher. (It will be whitespace-stripped right and left.)",
    )
    parser.add_argument(
        "--method",
        choices=[
            HashMethods.HMAC_MD5,
            HashMethods.HMAC_SHA256,
            HashMethods.HMAC_SHA512,
        ],
        default=HashMethods.HMAC_MD5,
        help="Hash method",
    )
    parser.add_argument(
        "--ntests",
        type=int,
        default=100000,
        help="Number of hash tests to time for real (a small number).",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=10,
        help="Length of string to hash. (Consecutive integers covering the "
        "range of --ntests will be padded to this length.)",
    )
    parser.add_argument(
        "--intended",
        type=int,
        nargs="+",
        default=[1000000000, 7300000000000, 36500000000000],
        help="Number of hash tests to calculate time for (a big number). For"
        "example, approx. 1000000000 (1e9) for NHS number; "
        "36500000000000 (3.65e13) for NHS number "
        "plus DOBs covering a century; "
        "7300000000000 (7.3e12) for NHS number "
        "plus DOBs covering two decades.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Be verbose (NB will write key to stderr)",
    )

    args = parser.parse_args()
    main_only_quicksetup_rootlogger(
        logging.DEBUG if args.verbose else logging.INFO
    )

    key = generate_random_string(length=64) if args.key is None else args.key

    test_hash_speed(
        output_filename=args.outfile,
        hash_method=args.method,
        key=key,
        string_length=args.length,
        ntests=args.ntests,
        intended_possibilities=args.intended,
    )


if __name__ == "__main__":
    main()
