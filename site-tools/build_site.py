#!/usr/bin/env python3
"""Retired full-site generator: refuse before writing any publication files.

Historical templates predate reviewed presentation changes. Git history retains
that implementation. The supported publication command is documented in
site-tools/VALIDATION.md; do not restore the old generator as a shortcut.
"""
import sys

if __name__ == '__main__':
    sys.exit('Retired full-site generator. No files changed. Use python site-tools/build_machine_access.py and the validation workflow in site-tools/VALIDATION.md.')
