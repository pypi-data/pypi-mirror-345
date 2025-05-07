###############################################################################
# (c) Copyright 2020-2022 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

__all__ = [
    "get_api_token",
    "wipe_token_cache",
    "hacks",
    "render_yaml",
    "parse_yaml",
    "validate_yaml",
    "lint_all",
    "validators",
    "write_jsroot_compression_options",
]

from os.path import join

from . import hacks, validators
from .linting import lint_all
from .parsing import parse_yaml, render_yaml, validate_yaml


def write_jsroot_compression_options(dynamic_dir):
    """Write options file to configure JSROOT-compatible compression on job output files.

    Args:
        dynamic_dir: Location to write the use-jsroot-compression.py options file.
    """
    with open(join(dynamic_dir, "use-jsroot-compression.py"), "wt") as fp:
        fp.write(
            "\n".join(
                [
                    "from Configurables import RootCnvSvc",
                    "RootCnvSvc().GlobalCompression = 'ZLIB:1'",
                    "",
                    "try:",
                    "    from Configurables import DaVinci",
                    "except ImportError:",
                    "    pass",
                    "else:",
                    "    try:",
                    "        DaVinci().RootCompressionLevel = 'ZLIB:1'",
                    "    except AttributeError:",
                    "        pass",
                ]
            )
        )
