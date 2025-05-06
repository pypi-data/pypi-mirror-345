"""
Mypy helper module to assist with type checking issues.

This module provides utilities to help users identify and fix common mypy issues.
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Initialize rich console
console = Console()

# Common mypy error patterns
ERROR_PATTERNS = {
    "missing_import": r"Cannot find implementation or library stub for module named '([^']+)'",
    "incompatible_types": r"Incompatible types in assignment \(expression has type \"([^\"]+)\", variable has type \"([^\"]+)\"\)",
    "missing_return_type": r"Function is missing a return type annotation",
    "missing_type_annotation": r"Variable \"([^\"]+)\" is not annotated",
    "need_type_annotation": r"Need type annotation for \"([^\"]+)\"",
    "optional_access": r"Item \"None\" of \"Optional\[([^]]+)\]\" has no attribute \"([^\"]+)\"",
    "union_access": r"Item \"([^\"]+)\" of \"Union\[([^]]+)\]\" has no attribute \"([^\"]+)\"",
}


class MypyIssue:
    """Class representing a mypy issue with suggested fixes."""

    def __init__(
        self,
        file: str,
        line: int,
        column: int,
        error_type: str,
        message: str,
        code_context: Optional[str] = None,
    ):
        self.file = file
        self.line = line
        self.column = column
        self.error_type = error_type
        self.message = message
        self.code_context = code_context
        self.suggested_fixes: List[str] = []
        self._analyze_issue()

    def _analyze_issue(self) -> None:
        """Analyze the issue and generate suggested fixes."""
        if "missing_import" in self.error_type:
            self._suggest_missing_import_fix()
        elif "incompatible_types" in self.error_type:
            self._suggest_incompatible_types_fix()
        elif "missing_return_type" in self.error_type:
            self._suggest_missing_return_type_fix()
        elif (
            "missing_type_annotation" in self.error_type
            or "need_type_annotation" in self.error_type
        ):
            self._suggest_missing_annotation_fix()
        elif "optional_access" in self.error_type:
            self._suggest_optional_access_fix()
        elif "union_access" in self.error_type:
            self._suggest_union_access_fix()

    def _suggest_missing_import_fix(self) -> None:
        """Suggest fixes for missing import issues."""
        match = re.search(ERROR_PATTERNS["missing_import"], self.message)
        if match:
            module_name = match.group(1)
            self.suggested_fixes.append(
                f"Install the package containing '{module_name}'"
            )
            self.suggested_fixes.append(
                f"Create a stub file for '{module_name}' using stubgen"
            )
            self.suggested_fixes.append(f"Add '# type: ignore' comment for this import")
            self.suggested_fixes.append(
                f"Create an empty .pyi file at '{module_name}.pyi'"
            )

    def _suggest_incompatible_types_fix(self) -> None:
        """Suggest fixes for incompatible types issues."""
        match = re.search(ERROR_PATTERNS["incompatible_types"], self.message)
        if match:
            expr_type, var_type = match.group(1), match.group(2)
            self.suggested_fixes.append(
                f"Cast the expression to '{var_type}' using typing.cast()"
            )
            self.suggested_fixes.append(
                f"Change the variable type annotation to 'Union[{var_type}, {expr_type}]'"
            )
            self.suggested_fixes.append(f"Add explicit type check before assignment")
            self.suggested_fixes.append(f"Add '# type: ignore' comment for this line")

    def _suggest_missing_return_type_fix(self) -> None:
        """Suggest fixes for missing return type issues."""
        if self.code_context:
            # Try to analyze the function to guess return type
            self.suggested_fixes.append("Add an explicit return type annotation")
            self.suggested_fixes.append(
                "Use 'None' as return type if function doesn't return a value"
            )
            self.suggested_fixes.append(
                "Use 'Any' as return type if return type is dynamic"
            )
            self.suggested_fixes.append(
                "Use 'monkeytype run <script.py>' to generate type annotations"
            )

    def _suggest_missing_annotation_fix(self) -> None:
        """Suggest fixes for missing type annotation issues."""
        pattern = (
            ERROR_PATTERNS["missing_type_annotation"]
            if "missing_type_annotation" in self.error_type
            else ERROR_PATTERNS["need_type_annotation"]
        )
        match = re.search(pattern, self.message)
        if match:
            var_name = match.group(1)
            self.suggested_fixes.append(f"Add type annotation for '{var_name}'")
            self.suggested_fixes.append(
                f"Use 'Any' as type if variable type is dynamic"
            )
            self.suggested_fixes.append(
                f"Use 'monkeytype run <script.py>' to generate type annotations"
            )

    def _suggest_optional_access_fix(self) -> None:
        """Suggest fixes for Optional access issues."""
        match = re.search(ERROR_PATTERNS["optional_access"], self.message)
        if match:
            type_name, attr = match.group(1), match.group(2)
            self.suggested_fixes.append(
                f"Add a None check before accessing attribute '{attr}'"
            )
            self.suggested_fixes.append(
                f"Use 'assert x is not None' before accessing the attribute"
            )
            self.suggested_fixes.append(
                f"Use the 'or' operator with a default value: 'x or default_value'"
            )
            self.suggested_fixes.append(
                f"Use conditional expression: 'x.{attr} if x is not None else default'"
            )

    def _suggest_union_access_fix(self) -> None:
        """Suggest fixes for Union access issues."""
        match = re.search(ERROR_PATTERNS["union_access"], self.message)
        if match:
            item_type, union_types, attr = (
                match.group(1),
                match.group(2),
                match.group(3),
            )
            self.suggested_fixes.append(
                f"Add a type check before accessing attribute '{attr}'"
            )
            self.suggested_fixes.append(
                f"Use 'isinstance(x, SpecificType)' before accessing the attribute"
            )
            self.suggested_fixes.append(f"Use typing.cast() to assert the type")
            self.suggested_fixes.append(
                f"Use TypeGuard to create a type-narrowing function"
            )


def run_mypy(
    target_path: Union[str, Path],
    config_file: Optional[Union[str, Path]] = None,
    strict: bool = False,
    verbose: bool = False,
    ignore_missing_imports: bool = True,
) -> Tuple[bool, List[MypyIssue]]:
    """
    Run mypy on the target path and collect issues.

    Args:
        target_path: Path to the directory or file to check
        config_file: Path to mypy config file
        strict: Whether to run mypy in strict mode
        verbose: Whether to show verbose output
        ignore_missing_imports: Whether to ignore missing imports

    Returns:
        Tuple of (success, list of issues)
    """
    target_path = Path(target_path)

    # Check if mypy is installed
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        console.print("[yellow]Mypy is not installed. Installing mypy...[/yellow]")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "mypy"], check=True)
        except subprocess.SubprocessError:
            console.print(
                "[red]Failed to install mypy. Please install it manually with 'pip install mypy'.[/red]"
            )
            return False, []

    cmd = ["mypy"]

    if config_file:
        cmd.extend(["--config-file", str(config_file)])

    if strict:
        cmd.append("--strict")

    if ignore_missing_imports:
        cmd.append("--ignore-missing-imports")

    cmd.append(str(target_path))

    if verbose:
        console.print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        success = result.returncode == 0

        if success and verbose:
            console.print("[green]No mypy issues found![/green]")
            return True, []

        # Parse mypy output
        issues = []
        for line in result.stdout.splitlines() + result.stderr.splitlines():
            # Parse error line format: file:line:column: error: message
            match = re.match(r"(.+):(\d+):(\d+): (\w+): (.+)", line)
            if match:
                file, line_num, col, error_type, message = match.groups()

                # Get code context if possible
                code_context = None
                try:
                    with open(file, "r") as f:
                        lines = f.readlines()
                        line_idx = int(line_num) - 1
                        if 0 <= line_idx < len(lines):
                            code_context = lines[line_idx].strip()
                except Exception:
                    pass

                issue = MypyIssue(
                    file=file,
                    line=int(line_num),
                    column=int(col),
                    error_type=error_type,
                    message=message,
                    code_context=code_context,
                )
                issues.append(issue)

        return success, issues

    except Exception as e:
        console.print(f"[red]Error running mypy: {e}[/red]")
        return False, []


def generate_stubs_for_module(
    module_name: str, output_dir: Optional[Path] = None
) -> bool:
    """
    Generate stub files for a module using stubgen.

    Args:
        module_name: Name of the module to generate stubs for
        output_dir: Directory to output stubs to

    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = ["stubgen", "-m", module_name]

        if output_dir:
            cmd.extend(["-o", str(output_dir)])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            console.print(
                f"[green]Successfully generated stubs for {module_name}[/green]"
            )
            return True
        else:
            console.print(f"[red]Failed to generate stubs: {result.stderr}[/red]")
            return False

    except Exception as e:
        console.print(f"[red]Error generating stubs: {e}[/red]")
        return False


def apply_monkeytype(
    script_path: Union[str, Path],
    module_name: Optional[str] = None,
    apply: bool = False,
) -> bool:
    """
    Run monkeytype on a script to generate type annotations.

    Args:
        script_path: Path to the script to run
        module_name: Name of the module to apply types to
        apply: Whether to apply the generated types

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if monkeytype is installed
        try:
            import monkeytype
        except ImportError:
            console.print("[yellow]MonkeyType not installed. Installing...[/yellow]")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "monkeytype"], check=True
            )

        # Run the script with monkeytype
        script_path = Path(script_path)
        run_cmd = [sys.executable, "-m", "monkeytype", "run", str(script_path)]

        console.print(f"Running: {' '.join(run_cmd)}")
        run_result = subprocess.run(
            run_cmd, capture_output=True, text=True, check=False
        )

        if run_result.returncode != 0:
            console.print(
                f"[red]Error running script with monkeytype: {run_result.stderr}[/red]"
            )
            return False

        # If apply is True and module_name is provided, apply the types
        if apply and module_name:
            apply_cmd = [sys.executable, "-m", "monkeytype", "apply", module_name]

            console.print(f"Applying types: {' '.join(apply_cmd)}")
            apply_result = subprocess.run(
                apply_cmd, capture_output=True, text=True, check=False
            )

            if apply_result.returncode != 0:
                console.print(f"[red]Error applying types: {apply_result.stderr}[/red]")
                return False

            console.print(f"[green]Successfully applied types to {module_name}[/green]")

        return True

    except Exception as e:
        console.print(f"[red]Error using monkeytype: {e}[/red]")
        return False


def display_mypy_issues(issues: List[MypyIssue], verbose: bool = False) -> None:
    """
    Display mypy issues in a formatted table.

    Args:
        issues: List of mypy issues
        verbose: Whether to show verbose output
    """
    if not issues:
        console.print("[green]No mypy issues found![/green]")
        return

    # Group issues by file
    issues_by_file: Dict[str, List[MypyIssue]] = {}
    for issue in issues:
        if issue.file not in issues_by_file:
            issues_by_file[issue.file] = []
        issues_by_file[issue.file].append(issue)

    # Display issues by file
    for file, file_issues in issues_by_file.items():
        console.print(
            Panel(f"[bold]{file}[/bold] - {len(file_issues)} issues", style="blue")
        )

        table = Table(show_header=True, header_style="bold")
        table.add_column("Line")
        table.add_column("Error")
        table.add_column("Message")
        if verbose:
            table.add_column("Suggested Fixes")

        for issue in file_issues:
            row = [str(issue.line), issue.error_type, issue.message]

            if verbose:
                fixes = "\n".join([f"- {fix}" for fix in issue.suggested_fixes])
                row.append(fixes)

            table.add_row(*row)

        console.print(table)


def fix_common_mypy_issues(
    target_path: Union[str, Path],
    auto_fix: bool = False,
    interactive: bool = True,
    verbose: bool = False,
) -> bool:
    """
    Identify and fix common mypy issues.

    Args:
        target_path: Path to the directory or file to check
        auto_fix: Whether to automatically apply fixes
        interactive: Whether to interactively prompt for fixes
        verbose: Whether to show verbose output

    Returns:
        True if all issues were fixed, False otherwise
    """
    target_path = Path(target_path)

    # Run mypy to get issues
    success, issues = run_mypy(target_path, verbose=verbose)

    if success:
        console.print("[green]No mypy issues found![/green]")
        return True

    # Display issues
    display_mypy_issues(issues, verbose=verbose)

    if not auto_fix and not interactive:
        return False

    # TODO: Implement auto-fixing logic
    # This would involve parsing and modifying Python files to add type annotations,
    # add None checks, etc. based on the issue type

    if interactive:
        # TODO: Implement interactive fixing logic
        # This would involve prompting the user for each issue and applying the selected fix
        pass

    return False


def add_type_ignore_comments(
    target_path: Union[str, Path], issues: List[MypyIssue], selective: bool = True
) -> int:
    """
    Add # type: ignore comments to lines with mypy issues.

    Args:
        target_path: Path to the directory or file
        issues: List of mypy issues
        selective: Whether to selectively add comments based on issue type

    Returns:
        Number of comments added
    """
    target_path = Path(target_path)

    # Group issues by file
    issues_by_file: Dict[str, List[MypyIssue]] = {}
    for issue in issues:
        if issue.file not in issues_by_file:
            issues_by_file[issue.file] = []
        issues_by_file[issue.file].append(issue)

    comments_added = 0

    # Process each file
    for file, file_issues in issues_by_file.items():
        try:
            with open(file, "r") as f:
                lines = f.readlines()

            modified = False

            # Add type: ignore comments to lines with issues
            for issue in file_issues:
                line_idx = issue.line - 1

                if line_idx < 0 or line_idx >= len(lines):
                    continue

                line = lines[line_idx]

                # Skip if already has a type: ignore comment
                if "# type: ignore" in line:
                    continue

                # Skip certain issues if selective is True
                if selective:
                    # Only add type: ignore for import errors and certain other cases
                    if (
                        "missing_import" not in issue.error_type
                        and "incompatible_types" not in issue.error_type
                    ):
                        continue

                # Add comment at the end of the line
                if line.rstrip().endswith(":"):
                    # Don't add type: ignore to lines ending with colon (class/function definitions)
                    continue

                lines[line_idx] = line.rstrip() + "  # type: ignore\n"
                modified = True
                comments_added += 1

            # Write modified file
            if modified:
                with open(file, "w") as f:
                    f.writelines(lines)

        except Exception as e:
            console.print(f"[red]Error processing file {file}: {e}[/red]")

    return comments_added


def create_mypy_config(
    target_dir: Union[str, Path],
    strict: bool = False,
    ignore_missing_imports: bool = True,
    disallow_untyped_defs: bool = False,
    disallow_incomplete_defs: bool = False,
) -> Path:
    """
    Create a mypy configuration file.

    Args:
        target_dir: Directory to create the config file in
        strict: Whether to enable strict mode
        ignore_missing_imports: Whether to ignore missing imports
        disallow_untyped_defs: Whether to disallow untyped function definitions
        disallow_incomplete_defs: Whether to disallow incomplete function definitions

    Returns:
        Path to the created config file
    """
    target_dir = Path(target_dir)
    config_path = target_dir / "mypy.ini"

    config_content = "[mypy]\n"

    if strict:
        config_content += "strict = True\n"
    else:
        if ignore_missing_imports:
            config_content += "ignore_missing_imports = True\n"

        if disallow_untyped_defs:
            config_content += "disallow_untyped_defs = True\n"

        if disallow_incomplete_defs:
            config_content += "disallow_incomplete_defs = True\n"

    # Add some reasonable defaults
    config_content += "check_untyped_defs = True\n"
    config_content += "warn_redundant_casts = True\n"
    config_content += "warn_unused_ignores = True\n"
    config_content += "warn_return_any = True\n"

    # Write config file
    with open(config_path, "w") as f:
        f.write(config_content)

    console.print(f"[green]Created mypy config file at {config_path}[/green]")

    return config_path
