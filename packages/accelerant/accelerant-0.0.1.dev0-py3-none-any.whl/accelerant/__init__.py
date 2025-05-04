#!/usr/bin/env python
#   
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2025 Scientific Automation Innovations.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/Scientific-AI/accelerant/blob/master/LICENSE

# author, version, license, and long description
try: # the package is installed
    from .__info__ import __version__, __author__, __doc__, __license__
except: # pragma: no cover
    import os
    import sys
    parent = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    sys.path.append(parent)
    # get distribution meta info
    from version import (__version__, __author__,
                         get_license_text, get_readme_as_rst)
    __license__ = get_license_text(os.path.join(parent, 'LICENSE'))
    __license__ = "\n%s" % __license__
    __doc__ = get_readme_as_rst(os.path.join(parent, 'README.md'))
    del os, sys, parent, get_license_text, get_readme_as_rst


def license():
    """print the license"""
    print(__license__)
    return

# end of file
