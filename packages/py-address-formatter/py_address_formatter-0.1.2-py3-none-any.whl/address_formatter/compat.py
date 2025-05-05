#!/usr/bin/env python3
"""
Backward compatibility script for the address formatter CLI.

This script provides backward compatibility for the old 'address-formatter'
command, redirecting to the new 'py-address-formatter' command.
"""

import sys
import warnings
from .cli import main

if __name__ == "__main__":
    warnings.warn(
        "The 'address-formatter' command is deprecated. Please use 'py-address-formatter' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    main()
