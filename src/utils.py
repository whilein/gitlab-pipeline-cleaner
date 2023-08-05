#     Copyright 2023 Whilein
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import re
from datetime import timedelta

# https://gist.github.com/santiagobasulto/698f0ff660968200f873a2f9d1c4113c

TIMEDELTA_PATTERN = re.compile(
    (r'((?P<days>\d+)d)?'
     r'((?P<hours>\d+)h)?'
     r'((?P<minutes>\d+)m)?'),
    re.IGNORECASE
)

UNITS = {
    'd': 24 * 60 * 60,
    'h': 60 * 60,
    'm': 60,
    's': 1
}


def write_timedelta(td: timedelta) -> str:
    if td == 0:
        return ''

    s = ''
    total_seconds = td.total_seconds()

    for unit, value in UNITS.items():
        if total_seconds >= value:
            units = int(total_seconds / value)
            s += str(units) + unit
            total_seconds -= value * units

    return s


def read_timedelta(text: str) -> timedelta:
    if text == '-':
        return timedelta(seconds=0)

    match = TIMEDELTA_PATTERN.match(text)

    if match:
        parts = {k: int(v) for k, v in match.groupdict().items() if v}
        return timedelta(**parts)
