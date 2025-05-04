# Pygnuregex, GNU-style regex for Python
# Copyright (C) 2025  Nikolaos Chatzikonstantinou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ctypes
import ctypes.util
from enum import IntEnum
from pathlib import Path
import platform
import threading
from typing import Generator

# Protect syntax options during the compilation of a regex; the global
# variable is an unfortunate feature of <regex.h>.
syntax_mutex = threading.Lock()

libc_path = ctypes.util.find_library("c")
libc = ctypes.CDLL(libc_path)
ext = {"Linux": ".so", "Darwin": ".dylib", "Windows": ".dll"}.get(
    platform.system(), ".so"
)
stub_path = Path(__file__).parent / f"stub{ext}"
stub = ctypes.CDLL(str(stub_path))

# Set global state of syntax options.
stub.pygnuregex_set_syntax_options.restype = None
# Allocation.
libc.free.restype = None
libc.regfree.restype = None
stub.pygnuregex_make_pattern_buffer.restype = ctypes.c_void_p
stub.pygnuregex_make_registers.restype = ctypes.c_void_p
# Syntax flags.
stub.pygnuregex_get_BACKSLASH_ESCAPE_IN_LISTS.restype = ctypes.c_ulong
stub.pygnuregex_get_BK_PLUS_QM.restype = ctypes.c_ulong
stub.pygnuregex_get_CHAR_CLASSES.restype = ctypes.c_ulong
stub.pygnuregex_get_CONTEXT_INDEP_ANCHORS.restype = ctypes.c_ulong
stub.pygnuregex_get_CONTEXT_INDEP_OPS.restype = ctypes.c_ulong
stub.pygnuregex_get_CONTEXT_INVALID_DUP.restype = ctypes.c_ulong
stub.pygnuregex_get_CONTEXT_INVALID_OPS.restype = ctypes.c_ulong
stub.pygnuregex_get_DEBUG.restype = ctypes.c_ulong
stub.pygnuregex_get_DOT_NEWLINE.restype = ctypes.c_ulong
stub.pygnuregex_get_DOT_NOT_NULL.restype = ctypes.c_ulong
stub.pygnuregex_get_HAT_LISTS_NOT_NEWLINE.restype = ctypes.c_ulong
stub.pygnuregex_get_ICASE.restype = ctypes.c_ulong
stub.pygnuregex_get_INTERVALS.restype = ctypes.c_ulong
stub.pygnuregex_get_INVALID_INTERVAL_ORD.restype = ctypes.c_ulong
stub.pygnuregex_get_LIMITED_OPS.restype = ctypes.c_ulong
stub.pygnuregex_get_NEWLINE_ALT.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_BK_BRACES.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_BK_PARENS.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_BK_REFS.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_BK_VBAR.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_EMPTY_RANGES.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_GNU_OPS.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_POSIX_BACKTRACKING.restype = ctypes.c_ulong
stub.pygnuregex_get_NO_SUB.restype = ctypes.c_ulong
stub.pygnuregex_get_UNMATCHED_RIGHT_PAREN_ORD.restype = ctypes.c_ulong
# Predefined composite syntaxes.
stub.pygnuregex_get_SYNTAX_EMACS.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_AWK.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_AWK.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_GREP.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_EGREP.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_EGREP.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_ED.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_SED.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_COMMON.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_BASIC.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_MINIMAL_BASIC.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_EXTENDED.restype = ctypes.c_ulong
stub.pygnuregex_get_SYNTAX_POSIX_MINIMAL_EXTENDED.restype = ctypes.c_ulong
# Compile, match, and search.
stub.pygnuregex_compile.restype = ctypes.c_char_p
# Getters.
stub.pygnuregex_get_nsub.restype = ctypes.c_size_t
stub.pygnuregex_get_num_regs.restype = ctypes.c_size_t

# Set default syntax options to 0.
stub.pygnuregex_set_syntax_options(0)


class Pattern:
    """A regex pattern buffer, including its match information."""

    def __init__(self):
        self.pb = stub.pygnuregex_make_pattern_buffer()
        self.m_span = []
        self.m_nsub = 0
        if self.pb is None:
            raise MemoryError("Out of memory in pygnuregex_make_pattern_buffer()!")
        self.regs = stub.pygnuregex_make_registers()
        if self.regs is None:
            libc.free(self.pb)
            raise MemoryError("Out of memory in pygnuregex_make_registers()!")

    def __del__(self):
        libc.regfree(self.pb)
        libc.free(self.pb)
        libc.free(self.regs)
        self.pb = ctypes.c_void_p(None)
        self.regs = ctypes.c_void_p(None)

    def match(self, string: bytes, start: int = 0) -> int:
        """Attempt to match the pattern against the (binary) string.

        Returns the number of bytes matched.
        """
        result = stub.pygnuregex_match(
            self.pb,
            string,
            ctypes.c_int(len(string)),
            ctypes.c_int(start),
            self.regs,
        )
        if result == -1:
            # No match
            self.m_span = []
            return -1
        elif result == -2:
            # Internal error
            raise RuntimeError("re_match(): Internal error")
        else:
            # Match.
            n = stub.pygnuregex_get_num_regs(self.regs)
            self.m_span = [
                (
                    stub.pygnuregex_get_start(self.regs, ctypes.c_size_t(i)),
                    stub.pygnuregex_get_end(self.regs, ctypes.c_size_t(i)),
                )
                for i in range(n - 1)
            ]
            return result

    def search(self, string: bytes, start: int = 0) -> int:
        """Attempt to search the pattern in the (binary) string.

        Returns the index of the match.
        """
        result = stub.pygnuregex_search(
            self.pb,
            string,
            ctypes.c_int(len(string)),
            ctypes.c_int(start),
            ctypes.c_int(len(string) - start),
            self.regs,
        )
        if result == -1:
            # No match
            self.m_span = []
            return -1
        elif result == -2:
            # Internal error
            raise RuntimeError("re_search(): Internal error")
        else:
            # Match.
            n = stub.pygnuregex_get_num_regs(self.regs)
            self.m_span = [
                (
                    stub.pygnuregex_get_start(self.regs, ctypes.c_size_t(i)),
                    stub.pygnuregex_get_end(self.regs, ctypes.c_size_t(i)),
                )
                for i in range(n - 1)
            ]
            return result

    def span(self) -> list[tuple[int, int]]:
        """The list of group spans. First is whole match."""
        return self.m_span

    def nsub(self) -> int:
        """The number of parenthetical subexpressions in the regex."""
        return self.m_nsub

    def finditer(
        self, string: bytes, start: int = 0
    ) -> Generator[list[tuple[int, int]], None, None]:
        """A generator of all matches."""
        while True:
            if self.search(string, start) == -1:
                break
            span = self.span()
            start, end = span[0]
            if start == end:
                # Avoid infinite loops on zero-length matches.
                start = end + 1
            else:
                start = end
            yield span


class SyntaxFlag(IntEnum):
    """Syntax options, logical-OR may be applied to choose multiple."""

    RE_BACKSLASH_ESCAPE_IN_LISTS = stub.pygnuregex_get_BACKSLASH_ESCAPE_IN_LISTS()
    RE_BK_PLUS_QM = stub.pygnuregex_get_BK_PLUS_QM()
    RE_CHAR_CLASSES = stub.pygnuregex_get_CHAR_CLASSES()
    RE_CONTEXT_INDEP_ANCHORS = stub.pygnuregex_get_CONTEXT_INDEP_ANCHORS()
    RE_CONTEXT_INDEP_OPS = stub.pygnuregex_get_CONTEXT_INDEP_OPS()
    RE_CONTEXT_INVALID_DUP = stub.pygnuregex_get_CONTEXT_INVALID_DUP()
    RE_CONTEXT_INVALID_OPS = stub.pygnuregex_get_CONTEXT_INVALID_OPS()
    RE_DEBUG = stub.pygnuregex_get_DEBUG()
    RE_DOT_NEWLINE = stub.pygnuregex_get_DOT_NEWLINE()
    RE_DOT_NOT_NULL = stub.pygnuregex_get_DOT_NOT_NULL()
    RE_HAT_LISTS_NOT_NEWLINE = stub.pygnuregex_get_HAT_LISTS_NOT_NEWLINE()
    RE_ICASE = stub.pygnuregex_get_ICASE()
    RE_INTERVALS = stub.pygnuregex_get_INTERVALS()
    RE_INVALID_INTERVAL_ORD = stub.pygnuregex_get_INVALID_INTERVAL_ORD()
    RE_LIMITED_OPS = stub.pygnuregex_get_LIMITED_OPS()
    RE_NEWLINE_ALT = stub.pygnuregex_get_NEWLINE_ALT()
    RE_NO_BK_BRACES = stub.pygnuregex_get_NO_BK_BRACES()
    RE_NO_BK_PARENS = stub.pygnuregex_get_NO_BK_PARENS()
    RE_NO_BK_REFS = stub.pygnuregex_get_NO_BK_REFS()
    RE_NO_BK_VBAR = stub.pygnuregex_get_NO_BK_VBAR()
    RE_NO_EMPTY_RANGES = stub.pygnuregex_get_NO_EMPTY_RANGES()
    RE_NO_GNU_OPS = stub.pygnuregex_get_NO_GNU_OPS()
    RE_NO_POSIX_BACKTRACKING = stub.pygnuregex_get_NO_POSIX_BACKTRACKING()
    RE_NO_SUB = stub.pygnuregex_get_NO_SUB()
    RE_UNMATCHED_RIGHT_PAREN_ORD = stub.pygnuregex_get_UNMATCHED_RIGHT_PAREN_ORD()
    RE_SYNTAX_EMACS = stub.pygnuregex_get_SYNTAX_EMACS()
    RE_SYNTAX_AWK = stub.pygnuregex_get_SYNTAX_AWK()
    RE_SYNTAX_POSIX_AWK = stub.pygnuregex_get_SYNTAX_POSIX_AWK()
    RE_SYNTAX_GREP = stub.pygnuregex_get_SYNTAX_GREP()
    RE_SYNTAX_EGREP = stub.pygnuregex_get_SYNTAX_EGREP()
    RE_SYNTAX_POSIX_EGREP = stub.pygnuregex_get_SYNTAX_POSIX_EGREP()
    RE_SYNTAX_ED = stub.pygnuregex_get_SYNTAX_ED()
    RE_SYNTAX_SED = stub.pygnuregex_get_SYNTAX_SED()
    RE_SYNTAX_POSIX_COMMON = stub.pygnuregex_get_SYNTAX_POSIX_COMMON()
    RE_SYNTAX_POSIX_BASIC = stub.pygnuregex_get_SYNTAX_POSIX_BASIC()
    RE_SYNTAX_POSIX_MINIMAL_BASIC = stub.pygnuregex_get_SYNTAX_POSIX_MINIMAL_BASIC()
    RE_SYNTAX_POSIX_EXTENDED = stub.pygnuregex_get_SYNTAX_POSIX_EXTENDED()
    RE_SYNTAX_POSIX_MINIMAL_EXTENDED = (
        stub.pygnuregex_get_SYNTAX_POSIX_MINIMAL_EXTENDED()
    )


def compile(regex: bytes, syntax_flags: int = 0) -> Pattern:
    """Compile a regex pattern with given syntax options."""
    p = Pattern()
    with syntax_mutex:
        stub.pygnuregex_set_syntax_options(ctypes.c_ulong(syntax_flags))
        err = stub.pygnuregex_compile(regex, ctypes.c_int(len(regex)), p.pb)
    if err:
        raise RuntimeError(str(err, encoding="utf-8"))
    else:
        p.m_nsub = stub.pygnuregex_get_nsub(p.pb)
    return p
