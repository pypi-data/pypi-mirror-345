# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import os
import sys

__all__ = ['ANSI']


# ====
# ANSI
# ====

class ANSI(object):
    """
    ANSI escape codes for colors and styles.
    """

    if sys.platform == "win32":
        # Enables ANSI escape codes in some Windows terminals
        os.system("")

    # Style
    RESET = '\033[0m'
    BOLD = '\033[1m'
    FAINT = '\033[2m'
    ITALIC = '\033[3m'
    UNDERSCORE = '\033[4m'
    BLINK = '\033[5m'
    INVERSE = '\033[7m'
    BLINK_OFF = '\033[25m'
    INVERSE_OFF = '\033[27m'

    # Darker foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Darker background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Bright foreground colors
    BR_BLACK = '\033[90m'
    BR_RED = '\033[91m'
    BR_GREEN = '\033[92m'
    BR_YELLOW = '\033[93m'
    BR_BLUE = '\033[94m'
    BR_MAGENTA = '\033[95m'
    BR_CYAN = '\033[96m'
    BR_WHITE = '\033[97m'

    # Bright background colors
    BR_BG_BLACK = '\033[100m'
    BR_BG_RED = '\033[101m'
    BR_BG_GREEN = '\033[102m'
    BR_BG_YELLOW = '\033[103m'
    BR_BG_BLUE = '\033[104m'
    BR_BG_MAGENTA = '\033[105m'
    BR_BG_CYAN = '\033[106m'
    BR_BG_WHITE = '\033[107m'
