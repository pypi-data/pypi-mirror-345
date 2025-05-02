from src.aix import cmd
import pytest


@pytest.mark.parametrize(
    "command, expected_warnings, test_id",
    [
        # Happy path tests
        ("ls -l", [], "happy_path_safe_command"),
        ("echo 'Hello, world!'", [], "happy_path_safe_command_with_quotes"),
        ("git status", [], "happy_path_safe_git_command"),
        ("echo $HOME", [], "happy_path_environment_variable"),
        ("./my_script.sh", [], "happy_path_custom_script"),

        # Edge cases
        ("", [], "edge_case_empty_command"),
        ("   ", [], "edge_case_whitespace_command"),
        ("echo 'unclosed quote", ["Could not parse command safely"], "edge_case_unclosed_quote"),
        ("rm --help", ["Potentially dangerous command: rm"], "edge_case_dangerous_command_with_help"),
        ("git checkout -b my_branch", [], "edge_case_safe_git_command_with_flags"),

        # Error cases
        ("rm -rf /", ["Potentially dangerous command: rm", "Recursive flag detected: -rf"], "error_case_dangerous_command"),
        ("chmod -R 777 /", ["Potentially dangerous command: chmod", "Recursive flag detected: -R"], "error_case_recursive_chmod"),
        ("git clean -fd", ["Potentially dangerous git operation: git clean"], "error_case_dangerous_git_command"),
        ("sudo rm -rf /", ["Potentially dangerous command: sudo", "Potentially dangerous command: rm", "Recursive flag detected: -rf"], "error_case_sudo_dangerous_command"),  # sudo is handled by checking the base command (rm)
        ("dd if=/dev/zero of=/dev/null", ["Potentially dangerous command: dd"], "error_case_dd"),
    ],
)
def test_is_potentially_dangerous(command, expected_warnings, test_id):
    # Act
    warnings = cmd.is_potentially_dangerous(command)

    # Assert
    assert warnings == expected_warnings
