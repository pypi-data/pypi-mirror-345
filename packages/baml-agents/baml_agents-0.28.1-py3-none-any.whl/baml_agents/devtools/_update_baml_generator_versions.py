#!/usr/bin/env -S uv run
import argparse
import re
import subprocess
import sys
import traceback
from pathlib import Path

# Regex to find the simple version pattern
# (version\s*") : Group 1 (literal 'version "')
# ([^"]+)       : Group 2 (the current version string)
# (")           : Group 3 (the closing quote)
VERSION_PATTERN = re.compile(r'(version\s*")([^"]+)(")')

# Regex to check if a line starts a generator block
# \s*           : Optional leading whitespace
# generator     : Literal keyword
# \s+           : One or more whitespace chars
# [\w\d_-]+     : The generator name (alphanumeric, underscore, hyphen)
# \s*           : Optional whitespace before {
# \{            : The opening brace
# \s*$          : Optional trailing whitespace until end of line
GENERATOR_BLOCK_START_PATTERN = re.compile(r"^\s*generator\s+[\w\d_-]+\s*\{\s*$")


def update_version_in_file(*, file_path: Path, new_version: str, verbose: bool) -> bool:
    """
    Reads a file, finds 'version "YYY"' lines ONLY within generator blocks,
    replaces YYY with new_version, and writes the file back if changed.

    Args:
        file_path (Path): The path to the .baml file.
        new_version (str): The new version string to set.
        verbose (bool): Whether to print detailed output.

    Return:
        bool: True if the file was modified, False otherwise.

    """
    try:
        if verbose:
            print(f"Processing: {file_path}")
        # Use Path object's methods for reading/writing
        original_content = file_path.read_text(encoding="utf-8")

        modified_content = original_content
        modification_made = False
        matches_found_count = 0
        # Keep track of matches *actually* needing replacement inside generators
        matches_replaced_in_generator = 0

        # --- Replacement Function ---
        def replace_if_in_generator_block(match):
            nonlocal modification_made, matches_found_count, matches_replaced_in_generator
            matches_found_count += 1  # Count every potential version line found

            old_version = match.group(2)
            # Optimization: If version already matches, no need for context check
            if old_version == new_version:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match.start()}, already matches target. Skipping."
                    )
                return match.group(0)  # Return the original matched text

            match_start_index = match.start()

            # --- Context Check ---
            last_open_brace_index = original_content.rfind("{", 0, match_start_index)
            last_close_brace_index = original_content.rfind("}", 0, match_start_index)

            # Check if we are inside any block ({ exists before match)
            if last_open_brace_index == -1:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index}, but no preceding '{{'. Skipping."
                    )
                return match.group(0)

            # Check if the last block we entered is still open (no } after the last {)
            if last_close_brace_index > last_open_brace_index:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index}, but last relevant block closed @ pos {last_close_brace_index}. Skipping."
                    )
                return match.group(0)

            # Find the start of the line containing the opening brace
            block_header_start_index = (
                original_content.rfind("\n", 0, last_open_brace_index) + 1
            )

            # Extract the content of the line containing the opening brace
            # Find the end of that line
            block_header_line_end = original_content.find(
                "\n", block_header_start_index
            )
            if block_header_line_end == -1:  # Handle case where header is last line
                block_header_line_end = len(original_content)

            # Slice the line content up to and including the opening brace '{'
            # Strip leading/trailing whitespace for robust matching
            block_header_line_content = original_content[
                block_header_start_index : last_open_brace_index
                + 1  # Include the brace for regex
            ].strip()

            # Match the extracted header line against the generator pattern
            if GENERATOR_BLOCK_START_PATTERN.match(block_header_line_content):
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index} inside a generator block. Replacing with '{new_version}'."
                    )
                modification_made = True
                matches_replaced_in_generator += 1  # Count successful replacement
                return f"{match.group(1)}{new_version}{match.group(3)}"
            # The block is not a generator block
            if verbose:
                print(
                    f"  - Found version '{old_version}' @ pos {match_start_index}, but not in a 'generator' block (header line segment: '{block_header_line_content}'). Skipping."
                )
            return match.group(0)

        # --- End of Replacement Function ---

        modified_content = VERSION_PATTERN.sub(
            replace_if_in_generator_block, original_content
        )

        if modification_made:
            if verbose:
                print(f"  Updating file '{file_path}'...")
            # Use Path object's write_text method
            file_path.write_text(modified_content, encoding="utf-8")
            if verbose:
                print(f"  Successfully updated: {file_path}")
            return True  # Indicate modification happened

        # If no modification was made, but we did find patterns, report differently based on verbose
        if matches_found_count > 0:
            if verbose:
                if matches_replaced_in_generator == 0:
                    print(
                        f"  Found {matches_found_count} 'version \"...\"' pattern(s), but none required updates in generator blocks or they already matched."
                    )
                # If matches_replaced_in_generator > 0, the 'Updating file' message already printed.
            return False  # No modification *written* to disk
        else:  # No version patterns found at all
            if verbose:
                print(f"  No 'version \"...\"' pattern found at all in {file_path}.")
            return False

    except FileNotFoundError:
        if verbose:
            print(f"  Error: File not found: {file_path}", file=sys.stderr)
        return False
    except PermissionError:
        if verbose:
            print(f"  Error: Permission denied for file: {file_path}", file=sys.stderr)
        return False
    except Exception as e:
        if verbose:
            print(
                f"  An unexpected error occurred processing {file_path}: {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        return False


def update_baml_generator_versions():
    parser = argparse.ArgumentParser(
        description="Recursively find 'baml_src' folders and update the version string "
        "in 'version \"...\"' lines ONLY within 'generator ... {}' blocks inside .baml files."
    )
    parser.add_argument(
        "--search-root-path",
        required=False,
        default=str(Path.cwd()),
        help="The root folder path to search within. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--target-version",
        required=False,
        help="The new version string (e.g., '0.123.0'). Defaults to the installed baml-py version.",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        choices=["true", "false"],
        default="false",
        help="Set to 'true' for detailed output, 'false' for summary only.",
    )

    args = parser.parse_args()

    # Determine the new version, running subprocess only if not provided
    if args.target_version is None:
        installed_version = subprocess.run(  # noqa: S603
            ["uv", "pip", "list"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )
        baml_py_version = next(
            (
                line.split()[1]
                for line in installed_version.stdout.splitlines()
                if "baml-py" in line
            ),
            None,
        )
        if baml_py_version is None:
            print(
                "Error: baml-py version not found in pip list output.",
                file=sys.stderr,
            )
            sys.exit(1)
        new_version = baml_py_version
    else:
        new_version = str(args.target_version)
    new_version = new_version.replace('"', "").replace("'", "").strip()

    # Convert string path argument to a Path object
    root_folder = Path(args.search_root_path)
    # Convert verbose string to boolean
    verbose = args.verbose.lower() == "true"

    # Use Path object's is_dir() method
    if not root_folder.is_dir():
        print(
            f"Error: Folder not found or is not a directory: {root_folder}",
            file=sys.stderr,
        )
        sys.exit(1)

    if verbose:
        print(f"Starting search in: {root_folder}")
        print(f"Target version: {new_version}")
        print("-" * 30)

    found_baml_src = False
    updated_files_count = 0
    processed_baml_src_dirs = set()  # Keep track of printed directories

    # Use pathlib's rglob to find all items recursively, then filter
    for item in root_folder.rglob(
        "*.baml"
    ):  # More efficient: only glob for .baml files
        # Check if the parent directory is named 'baml_src'
        if item.is_file() and item.parent.name == "baml_src":
            current_baml_src_dir = item.parent
            if not found_baml_src:
                found_baml_src = True  # Mark that we found at least one

            # Only print the baml_src directory message once per directory if verbose
            if verbose and current_baml_src_dir not in processed_baml_src_dirs:
                print(f"\n--- Found baml_src directory: {current_baml_src_dir} ---")
                processed_baml_src_dirs.add(current_baml_src_dir)

            # Pass the Path object and verbose flag directly to the update function
            if update_version_in_file(
                file_path=item, new_version=new_version, verbose=verbose
            ):
                updated_files_count += 1

    if verbose:
        print("-" * 30)  # Print separator only if verbose mode printed details before

    # Final summary - always printed
    if not found_baml_src:
        print(
            "Warning: No directories named 'baml_src' were found containing .baml files."
        )
    elif updated_files_count == 0:
        print(
            "Finished: Found 'baml_src' directories, but no files required updates (or versions already matched)."
        )
    else:
        print(f"Finished: Successfully updated {updated_files_count} file(s).")


if __name__ == "__main__":
    update_baml_generator_versions()
