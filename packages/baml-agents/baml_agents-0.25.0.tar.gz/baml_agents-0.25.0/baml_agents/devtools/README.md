# Developer Tools (`devtools`)

This directory contains utility scripts designed to assist with the development, maintenance, and usage workflows related to the `baml-agents` project and projects that depend on it.

These tools are primarily intended for users looking to streamline tasks in their own projects that use `baml-agents` or BAML itself.

## Available Tools

### 1. `update-baml` (Update BAML Generator Versions)

**Description:**

Automates the process of updating the `version` specified within `generator` blocks across multiple `.baml` files. This is useful after upgrading the `baml-py` dependency to ensure your BAML files reference the correct generator version.

**Usage:**

The script is typically run using `uvx`:

```bash
# Basic usage
uvx --from baml-agents update-baml --target-version <new_baml_version> --search-root-path <path_to_search>

# Example: Update all .baml files in the current directory and subdirectories to version 0.85.0
uvx --from baml-agents update-baml --target-version 0.85.0 --search-root-path . --verbose false
```

**Arguments:**

*   `--target-version`: (Optional) The new BAML version string (e.g., `0.85.0`) to set in the generator blocks.
*   `--search-root-path`: (Optional) The root directory from which to start recursively searching for `baml_src` folders containing `.baml` files.
*   `--verbose`: (Optional) Set to `true` for detailed output, `false` (default) for less output.

**Pro Tips:**

1.  **Update to Installed Version:** Automatically use the currently installed `baml-py` version:
    ```bash
    uvx --from baml-agents update-baml --target-version "$(uv pip list | grep baml-py | awk '{print $2}')" --search-root-path . --verbose false
    ```
2.  **Combine with Updates:** Add this command to a script after `uv sync --upgrade` for a one-step dependency update process.
3.  **Pinned Execution:** Consider running with a specific version of `baml-agents` if needed: `uvx --from baml-agents@0.22.1 update-baml ...` (evaluate pros/cons for your workflow).
4.  **Help:** Get detailed help and all options:
    ```bash
    uvx --from baml-agents update-baml --help
    ```

**Status:** Beta - Please report any issues or suggestions!
