"""A unified+ format based on the standard difflib.unified_diff."""

import difflib
import typing


def format_diff(a: str, b: str, fromfile: str = "a", tofile: str = "b") -> str:
    """Return a unified+ diff between two strings.

    Args:
        a: The first string to compare.
        b: The second string to compare.
        fromfile: The name of the first file.
        tofile: The name of the second file.
    """
    result = []
    last_line: typing.Optional[str] = None
    normalized_endings_a, normalized_endings_b = (
        a.rstrip("\r\n") + "\n",
        b.rstrip("\r\n") + "\n",
    )
    for line in difflib.unified_diff(
        a=normalized_endings_a.splitlines(),
        b=normalized_endings_b.splitlines(),
        fromfile=fromfile,
        tofile=tofile,
    ):
        if last_line and line:
            doing_a_substitution = last_line.startswith("-") and line.startswith("+")
            last_line_had_dangling_whitespace = last_line != last_line.rstrip()
            new_line_is_last_line_without_whitespace = last_line[1:].rstrip() == line[1:]
            if all(
                [
                    doing_a_substitution,
                    last_line_had_dangling_whitespace,
                    new_line_is_last_line_without_whitespace,
                    # differing_whitespace_is_dangling,
                ]
            ):
                highlight = "^" * (len(last_line) - len(last_line.rstrip()))
                result.append("?" + " " * (len(line) - 1) + highlight)

        result.append(line.rstrip())
        last_line = line

    if a != b:
        if a.rstrip("\r\n") == a:
            result.append(f"\\ No newline at end of file ({fromfile})")
        if b.rstrip("\r\n") == b:
            result.append(f"\\ No newline at end of file ({tofile})")

    if not result:
        return ""
    return "\n".join(result) + "\n"
