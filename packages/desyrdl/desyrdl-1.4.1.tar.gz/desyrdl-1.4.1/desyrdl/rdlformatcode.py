#!/usr/bin/env python
# --------------------------------------------------------------------------- #
#           ____  _____________  __                                           #
#          / __ \/ ____/ ___/\ \/ /                 _   _   _                 #
#         / / / / __/  \__ \  \  /                 / \ / \ / \                #
#        / /_/ / /___ ___/ /  / /               = ( M | S | K )=              #
#       /_____/_____//____/  /_/                   \_/ \_/ \_/                #
#                                                                             #
# --------------------------------------------------------------------------- #
# @copyright Copyright 2022 DESY
# SPDX-License-Identifier: Apache-2.0
# --------------------------------------------------------------------------- #
# @date 2022-01-14
# @author Lukasz Butkowski <lukasz.butkowski@desy.de>
# --------------------------------------------------------------------------- #

from markdown import Markdown


class DesyrdlMarkup(Markdown):
    """DesyRdl markup class.

    class to overload default Markdown parsing to disable it
    """

    def __init__(self):
        self.reset()

    def reset(self):
        return self

    def convert(self, source):
        self.text = source
        return source
