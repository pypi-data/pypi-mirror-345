import argparse
import os
import re
import shutil
import sys


def truncate(s, max_width):
    if len(s) > max_width:
        return s[: (max_width - 6)] + " [...]"
    return s


def print_table(items, bold_first_column=False):
    """
    Print a basic ASCII table of the provided 2d-array. Adds no fancy formatting, just ensures the columns are aligned.
    If you want to reuse this code please use package `tabulate` instead, it does the same thing but much better.
    """
    terminal_width = shutil.get_terminal_size().columns
    is_interactive = sys.stdout.isatty()

    column_widths = []
    for col_idx in range(len(items[0])):  # Assume all rows have same number of columns
        max_width = max(len(str(row[col_idx])) for row in items)
        column_widths.append(max_width)

    padding = 4  # Space between columns
    fixed_width = sum(column_widths[:-1]) + (len(column_widths) - 1) * padding
    last_col_width = terminal_width - fixed_width - padding

    ABS_MAX_LINE_LENGTH = 160

    for row in items:
        # Print all columns except last
        for col_idx, value in enumerate(row[:-1]):
            if col_idx == 0 and bold_first_column and is_interactive:
                print(f"  \033[36m{str(value)}\033[0m{' ' * (column_widths[col_idx] - len(str(value)))}", end="  ")
            else:
                print(f"  {str(value):<{column_widths[col_idx]}}", end="  ")

        # Handle last column with word wrapping
        last_col = str(row[-1])
        last_col = truncate(last_col, ABS_MAX_LINE_LENGTH - fixed_width)
        words = last_col.split()
        if not words:
            print("")
            continue
        current_line = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 <= last_col_width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    print(" ".join(current_line))
                    print(" " * fixed_width, end="")
                current_line = [word]
                current_length = len(word)

        if current_line:
            print(" ".join(current_line))


def parse_makefile(makefile):
    """
    Warning: This parser was written hastily and is not very robust. Patches to improve it are welcome.
    Designed for GNU-style makefiles.
    """
    targets = {}
    target_line_matches = list(
        re.finditer(
            r'^(?P<targets>[^#\s][a-zA-Z0-9 /_.\-"]+?) *:(?P<deps>[^#\n]*)(?:#\s*(?P<side_comment>.+))?$',
            makefile,
            re.MULTILINE,
        )
    )

    for line_match in target_line_matches:
        if line_match.group("deps") and line_match.group("deps")[0] == "=":
            continue

        target_names = [t.strip() for t in line_match.group("targets").split()]
        dependencies = [d.strip() for d in line_match.group("deps").strip().split() if d.strip()]
        side_comment = line_match.group("side_comment").strip() if line_match.group("side_comment") else None

        start_pos = line_match.end() + 1
        recipe_lines = []
        for line in makefile[start_pos:].split("\n"):
            if not line.startswith("\t"):
                break
            recipe_lines.append(line)
        recipe = "\n".join(recipe_lines) if recipe_lines else None
        inner_comment = None
        if recipe and recipe.lstrip().startswith("#"):
            # Get all initial comment lines
            comment_lines = []
            for line in recipe.split("\n"):
                line = line.lstrip()
                if not line.startswith("#"):
                    break
                comment_lines.append(line.lstrip("#").strip())
            inner_comment = "\n".join(comment_lines)

        pos = line_match.start()
        top_comment_match = re.search(r"(?:^|\n)(?P<full_comment>#\s*(?P<comment>[^\n]+))[^#\n]*$", makefile[:pos])
        top_comment = top_comment_match.group("comment") if top_comment_match else None

        fullmatch = (
            (top_comment_match.group() if top_comment_match else "") + line_match.group() + "\n" + (recipe or "")
        ).strip()

        for target_name in target_names:
            if target_name.startswith("."):
                continue
            targets[target_name] = {
                "top_comment": top_comment,
                "side_comment": side_comment,
                "inner_comment": inner_comment,
                "recipe": recipe,
                "dependencies": dependencies,
                "fullmatch": fullmatch,
            }
    return targets


def inject_help_target(makefile_path):
    with open(makefile_path) as f:
        content = f.read()

    help_match = re.search(r"^help:.*?\n(?:\t.*?\n)*", content, re.MULTILINE)
    if help_match:
        help_content = help_match.group()
        line_number = content[: help_match.start()].count("\n") + 1
        if "makehelp" in help_content:
            print(f"Warning: A makehelp help target already exists in {makefile_path}. Doing nothing.", file=sys.stderr)
            sys.exit(0)
        else:
            print(
                f"Error: A pre-existing 'help' target already exists in {makefile_path} (line {line_number}). "
                + "Remove it first.",
                file=sys.stderr,
            )
            sys.exit(1)

    help_target = (
        "\n\nhelp:  # Show makefile usage help message\n"
        "\t@# Run makehelp using python uv, if available, otherwise error.\n"
        "\t@(which uvx >/dev/null 2>&1 && uvx makehelp) || echo 'Error: Please run `pip install uv` first'\n"
    )

    phony_match = re.search(r"^\.PHONY:\s*(.*)$", content, re.MULTILINE)
    if phony_match:
        current_phonys = phony_match.group(1).strip()
        if "help" not in current_phonys.split():
            new_content = (
                content[: phony_match.start()] + f".PHONY: {current_phonys} help" + content[phony_match.end() :]
            )
            content = new_content
    else:
        content = ".PHONY: help\n\n" + content

    content += help_target

    with open(makefile_path, "w") as f:
        f.write(content)

    print(f"Successfully injected 'help' target into {makefile_path}. Try it with `make help`.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Process a Makefile and display help information")
    parser.add_argument(
        "--file",
        "--makefile",
        "-f",
        dest="makefile",
        help='Path to the Makefile (defaults to "Makefile" or "makefile" in current directory)',
    )
    parser.add_argument(
        "--inject",
        action="store_true",
        help="Inject a `help` target into the Makefile that calls makehelp (entirely optional)",
    )
    parser.add_argument("target", nargs="?", help="Print the full recipe (code) of a specific target")
    args = parser.parse_args()

    if args.makefile:
        makefile_path = args.makefile
    else:
        files = os.listdir(".")
        makefile_path = next((f for f in ["Makefile", "makefile"] if f in files), None)
        if not makefile_path:
            print("Error: Makefile not found")
            sys.exit(1)

    if args.inject:
        inject_help_target(makefile_path)
        sys.exit(0)

    with open(makefile_path) as f:
        makefile = f.read()

    parsed_makefile = parse_makefile(makefile)

    if args.target:
        # Special mode: Print the full recipe (code) for a specific target
        if args.target not in parsed_makefile:
            targets_str = ", ".join(parsed_makefile.keys())
            print(
                f"Error: Target '{args.target}' not found in Makefile. Available targets: {targets_str}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(parsed_makefile[args.target]["fullmatch"])
    else:
        # Normal mode: Print this makefile's target options (inferred)
        targets = [
            (
                name,
                (
                    details["top_comment"].lstrip("#").strip()
                    if details["top_comment"]
                    else (
                        details["side_comment"].lstrip("#").strip()
                        if details["side_comment"]
                        else details["inner_comment"].lstrip("#").strip() if details["inner_comment"] else ""
                    )
                ),
            )
            for name, details in parsed_makefile.items()
        ]

        print(f"Usage: make{f' -f {args.makefile}' if args.makefile else ''} [TARGET]\nTargets:")
        print_table(targets, bold_first_column=True)


if __name__ == "__main__":
    main()
