#!/usr/bin/env bash

# Shared predicates for `lint` and `lint-hook`.
#
# Sourced, never executed. Defines wb_lint_ignored(), the single answer to
# "may lint touch this path?" — consulted on EVERY code path, including the
# explicit-file-argument path, which previously had no exclusions at all and
# so rewrote vendored, hash-verified content handed to it by the hook.

# wb_lint_ignored <path>
#
# Returns 0 (ignore this file) when the path is in a directory lint must never
# touch, or when the repository's own .wblintignore / .markdownlintignore says so.
# Returns 1 (lint it) otherwise.
wb_lint_ignored() {
    local f="${1:-}" abs root ignore matched

    [ -n "$f" ] || return 1

    # Built-in exclusions, matched at ANY depth. The previous list lived only in
    # the --all branch and was anchored to the repo root ("./vendor/*"), so it
    # missed docs/vendor/, third_party/vendor/ and every other nested case.
    case "$f" in
        vendor/*|*/vendor/*) return 0 ;;
        node_modules/*|*/node_modules/*) return 0 ;;
        .git/*|*/.git/*) return 0 ;;
        .context/*|*/.context/*) return 0 ;;
        tmp/*|*/tmp/*) return 0 ;;
        .next/*|*/.next/*) return 0 ;;
        dist/*|*/dist/*) return 0 ;;
        build/*|*/build/*) return 0 ;;
    esac

    root="$(git rev-parse --show-toplevel 2>/dev/null)" || return 1
    [ -n "$root" ] || return 1

    # check-ignore resolves relative paths against -C, which is the repo root and
    # not necessarily our cwd. Make the path absolute so both agree.
    case "$f" in
        /*) abs="$f" ;;
        *)  abs="$PWD/$f" ;;
    esac

    for ignore in "$root/.wblintignore" "$root/.markdownlintignore"; do
        [ -f "$ignore" ] || continue
        # Reuse git's matcher rather than reimplementing gitignore semantics,
        # which are subtle enough to be their own bug source.
        #
        # core.excludesFile is ADDITIVE: the repository's own .gitignore still
        # applies. Honouring that would be wrong here — wb's own plan directories
        # under docs/plans/ are gitignored until promoted, and they are exactly
        # what the hook exists to lint. So -v is parsed and the match is only
        # accepted when it came from the file we passed in.
        matched="$(git -C "$root" -c core.excludesFile="$ignore" \
                       check-ignore -v --no-index -- "$abs" 2>/dev/null)" || matched=""
        case "$matched" in
            "$ignore":*) return 0 ;;
        esac
    done

    return 1
}
