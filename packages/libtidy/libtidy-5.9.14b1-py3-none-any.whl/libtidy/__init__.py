# Copyright (c) 2024 Adam Karpierz
# SPDX-License-Identifier: HTMLTIDY

from .__about__ import * ; del __about__  # noqa
from . import __config__ ; del __config__
from .__config__ import set_config as config

from ._tidy       import * ; del _tidy        # noqa
from ._tidybuffio import * ; del _tidybuffio  # noqa
from ._tidyenum   import * ; del _tidyenum    # noqa
