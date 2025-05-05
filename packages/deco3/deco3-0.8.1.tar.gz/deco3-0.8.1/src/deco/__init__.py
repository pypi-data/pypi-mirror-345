# Copyright (c) 2016 Alex Sherman
# Copyright (c) 2025 Adam Karpierz
# SPDX-License-Identifier: MIT

from .__about__ import * ; del __about__  # noqa

from . import conc

concurrent = conc.concurrent
synchronized = conc.synchronized
