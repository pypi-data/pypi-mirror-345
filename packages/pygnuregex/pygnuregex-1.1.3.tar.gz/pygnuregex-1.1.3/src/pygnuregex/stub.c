/* Stub functions for libc's GNU regex interface, useful for Python FFI.
 * Copyright (C) 2025  Nikolaos Chatzikonstantinou
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#define _GNU_SOURCE 1
#include <regex.h>

#include <stdlib.h>

/* Set global state of syntax options. */
void pygnuregex_set_syntax_options(unsigned long flags) {
  re_syntax_options = flags;
}
/* Allocation. */
void *pygnuregex_make_pattern_buffer(void) {
  struct re_pattern_buffer *p = malloc(sizeof(struct re_pattern_buffer));
  if (p) {
    p->translate = NULL;
    p->fastmap = NULL;
    p->buffer = NULL;
    p->allocated = 0;
  }
  return p;
}
void *pygnuregex_make_registers(void) {
  return malloc(sizeof(struct re_registers));
}
/* Syntax flags. */
unsigned long pygnuregex_get_BACKSLASH_ESCAPE_IN_LISTS(void) {
  return RE_BACKSLASH_ESCAPE_IN_LISTS;
}
unsigned long pygnuregex_get_BK_PLUS_QM(void) { return RE_BK_PLUS_QM; }
unsigned long pygnuregex_get_CHAR_CLASSES(void) { return RE_CHAR_CLASSES; }
unsigned long pygnuregex_get_CONTEXT_INDEP_ANCHORS(void) {
  return RE_CONTEXT_INDEP_ANCHORS;
}
unsigned long pygnuregex_get_CONTEXT_INDEP_OPS(void) {
  return RE_CONTEXT_INDEP_OPS;
}
unsigned long pygnuregex_get_CONTEXT_INVALID_DUP(void) {
  return RE_CONTEXT_INVALID_DUP;
}
unsigned long pygnuregex_get_CONTEXT_INVALID_OPS(void) {
  return RE_CONTEXT_INVALID_OPS;
}
unsigned long pygnuregex_get_DEBUG(void) { return RE_DEBUG; }
unsigned long pygnuregex_get_DOT_NEWLINE(void) { return RE_DOT_NEWLINE; }
unsigned long pygnuregex_get_DOT_NOT_NULL(void) { return RE_DOT_NOT_NULL; }
unsigned long pygnuregex_get_HAT_LISTS_NOT_NEWLINE(void) {
  return RE_HAT_LISTS_NOT_NEWLINE;
}
unsigned long pygnuregex_get_ICASE(void) { return RE_ICASE; }
unsigned long pygnuregex_get_INTERVALS(void) { return RE_INTERVALS; }
unsigned long pygnuregex_get_INVALID_INTERVAL_ORD(void) {
  return RE_INVALID_INTERVAL_ORD;
}
unsigned long pygnuregex_get_LIMITED_OPS(void) { return RE_LIMITED_OPS; }
unsigned long pygnuregex_get_NEWLINE_ALT(void) { return RE_NEWLINE_ALT; }
unsigned long pygnuregex_get_NO_BK_BRACES(void) { return RE_NO_BK_BRACES; }
unsigned long pygnuregex_get_NO_BK_PARENS(void) { return RE_NO_BK_PARENS; }
unsigned long pygnuregex_get_NO_BK_REFS(void) { return RE_NO_BK_REFS; }
unsigned long pygnuregex_get_NO_BK_VBAR(void) { return RE_NO_BK_VBAR; }
unsigned long pygnuregex_get_NO_EMPTY_RANGES(void) {
  return RE_NO_EMPTY_RANGES;
}
unsigned long pygnuregex_get_NO_GNU_OPS(void) { return RE_NO_GNU_OPS; }
unsigned long pygnuregex_get_NO_POSIX_BACKTRACKING(void) {
  return RE_NO_POSIX_BACKTRACKING;
}
unsigned long pygnuregex_get_NO_SUB(void) { return RE_NO_SUB; }
unsigned long pygnuregex_get_UNMATCHED_RIGHT_PAREN_ORD(void) {
  return RE_UNMATCHED_RIGHT_PAREN_ORD;
}
/* Predefined composite syntaxes. */
unsigned long pygnuregex_get_SYNTAX_EMACS(void) { return RE_SYNTAX_EMACS; }
unsigned long pygnuregex_get_SYNTAX_AWK(void) { return RE_SYNTAX_AWK; }
unsigned long pygnuregex_get_SYNTAX_POSIX_AWK(void) {
  return RE_SYNTAX_POSIX_AWK;
}
unsigned long pygnuregex_get_SYNTAX_GREP(void) { return RE_SYNTAX_GREP; }
unsigned long pygnuregex_get_SYNTAX_EGREP(void) { return RE_SYNTAX_EGREP; }
unsigned long pygnuregex_get_SYNTAX_POSIX_EGREP(void) {
  return RE_SYNTAX_POSIX_EGREP;
}
unsigned long pygnuregex_get_SYNTAX_ED(void) { return RE_SYNTAX_ED; }
unsigned long pygnuregex_get_SYNTAX_SED(void) { return RE_SYNTAX_SED; }
unsigned long pygnuregex_get_SYNTAX_POSIX_COMMON(void) {
  return _RE_SYNTAX_POSIX_COMMON;
}
unsigned long pygnuregex_get_SYNTAX_POSIX_BASIC(void) {
  return RE_SYNTAX_POSIX_BASIC;
}
unsigned long pygnuregex_get_SYNTAX_POSIX_MINIMAL_BASIC(void) {
  return RE_SYNTAX_POSIX_MINIMAL_BASIC;
}
unsigned long pygnuregex_get_SYNTAX_POSIX_EXTENDED(void) {
  return RE_SYNTAX_POSIX_EXTENDED;
}
unsigned long pygnuregex_get_SYNTAX_POSIX_MINIMAL_EXTENDED(void) {
  return RE_SYNTAX_POSIX_MINIMAL_EXTENDED;
}
/* Compile, match, and search. */
const char *pygnuregex_compile(const char *regex, const int regex_size,
                               struct re_pattern_buffer *pattern_buffer) {
  return re_compile_pattern(regex, regex_size, pattern_buffer);
}
int pygnuregex_match(struct re_pattern_buffer *pattern_buffer,
                     const char *string, const int size, const int start,
                     struct re_registers *regs) {
  return re_match(pattern_buffer, string, size, start, regs);
}
int pygnuregex_search(struct re_pattern_buffer *pattern_buffer,
                      const char *string, const int size, const int start,
                      const int range, struct re_registers *regs) {
  return re_search(pattern_buffer, string, size, start, range, regs);
}
/* Getters. */
size_t pygnuregex_get_nsub(struct re_pattern_buffer *p) { return p->re_nsub; }
size_t pygnuregex_get_num_regs(struct re_registers *regs) {
  return regs->num_regs;
}
int pygnuregex_get_start(struct re_registers *regs, size_t i) {
  return regs->start[i];
}
int pygnuregex_get_end(struct re_registers *regs, size_t i) {
  return regs->end[i];
}
