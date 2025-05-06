import os
import re
import json
import shutil
import logging
import difflib
import fnmatch
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from cli.coding.base import CodeMieTool
from cli.coding.models import (
    CommandLineInput,
    CreateDirectoryInput,
    DirectoryTreeInput,
    EditFileInput,
    EditOperation,
    FilesystemToolConfig,
    GetFileInfoInput,
    ListDirectoryInput,
    MoveFileInput,
    ReadFileInput,
    ReadMultipleFilesInput,
    SearchFilesInput,
    WriteFileInput,
)
from cli.coding.tools_vars import (
    COMMAND_LINE_TOOL,
    CREATE_DIRECTORY_TOOL,
    DEFAULT_IGNORE_PATTERNS,
    DIRECTORY_TREE_TOOL,
    EDIT_FILE_TOOL,
    GET_FILE_INFO_TOOL,
    LIST_ALLOWED_DIRECTORIES_TOOL,
    LIST_DIRECTORY_TOOL,
    MOVE_FILE_TOOL,
    READ_FILE_TOOL,
    READ_MULTIPLE_FILES_TOOL,
    SEARCH_FILES_TOOL,
    WRITE_FILE_TOOL,
)

logger = logging.getLogger(__name__)

class BaseFilesystemTool(CodeMieTool):
    """Base class for all filesystem tools with security validation."""

    filesystem_config: Optional[FilesystemToolConfig] = Field(exclude=True, default=None)

    def normalize_path(self, path: str) -> str:
        """Normalize path consistently."""
        return os.path.normpath(path)

    def expand_home(self, filepath: str) -> str:
        """Expand '~' to the user's home directory."""
        if filepath.startswith('~/') or filepath == '~':
            return os.path.join(os.path.expanduser('~'), filepath[1:] if len(filepath) > 1 else '')
        return filepath

    def _ensure_filesystem_config(self):
        """Ensure filesystem_config is properly initialized."""
        if not self.filesystem_config:
            self.filesystem_config = FilesystemToolConfig(allowed_directories=[os.getcwd()])
        elif not self.filesystem_config.allowed_directories:
            self.filesystem_config.allowed_directories = [os.getcwd()]

    def _is_path_in_allowed_dirs(self, path: str) -> bool:
        """Check if a path is within allowed directories."""
        return any(
            path.startswith(self.normalize_path(dir))
            for dir in self.filesystem_config.allowed_directories
        )

    def _validate_real_path(self, absolute_path: str) -> str:
        """Validate the real path (resolving symlinks)."""
        real_path = os.path.realpath(absolute_path)
        normalized_real = self.normalize_path(real_path)
        
        if not self._is_path_in_allowed_dirs(normalized_real):
            raise ValueError("Access denied - symlink target outside allowed directories")
            
        return real_path

    def _validate_parent_dir(self, absolute_path: str) -> str:
        """Validate the parent directory when the path itself doesn't exist."""
        parent_dir = os.path.dirname(absolute_path)
        try:
            real_parent_path = os.path.realpath(parent_dir)
            normalized_parent = self.normalize_path(real_parent_path)
            
            if not self._is_path_in_allowed_dirs(normalized_parent):
                raise ValueError("Access denied - parent directory outside allowed directories")
                
            return absolute_path
        except FileNotFoundError:
            raise ValueError(f"Parent directory does not exist: {parent_dir}")

    def validate_path(self, requested_path: str) -> str:
        """Validate that a path is within allowed directories."""
        self._ensure_filesystem_config()

        expanded_path = self.expand_home(requested_path)
        absolute = os.path.abspath(expanded_path)
        normalized_requested = self.normalize_path(absolute)

        if not self._is_path_in_allowed_dirs(normalized_requested):
            allowed_dirs = ', '.join(self.filesystem_config.allowed_directories)
            raise ValueError(f"Access denied - path outside allowed directories: {absolute} not in {allowed_dirs}")

        try:
            return self._validate_real_path(absolute)
        except FileNotFoundError:
            return self._validate_parent_dir(absolute)

    def integration_healthcheck(self) -> Tuple[bool, str]:
        if not self.filesystem_config:
            self.filesystem_config = FilesystemToolConfig(allowed_directories=[os.getcwd()])
        elif not self.filesystem_config.allowed_directories:
            self.filesystem_config.allowed_directories = [os.getcwd()]

        for dir_path in self.filesystem_config.allowed_directories:
            try:
                expanded_path = self.expand_home(dir_path)
                if not os.path.isdir(expanded_path):
                    return False, f"Path is not a directory: {dir_path}"
                if not os.access(expanded_path, os.R_OK):
                    return False, f"Directory is not accessible: {dir_path}"
            except Exception as e:
                return False, f"Error checking directory {dir_path}: {str(e)}"

        return True, ""


class ReadFileTool(BaseFilesystemTool):
    name: str = READ_FILE_TOOL.name
    args_schema: type[BaseModel] = ReadFileInput
    description: str = READ_FILE_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            with open(validated_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error reading file {path}: {str(e)}"


class ReadMultipleFilesTool(BaseFilesystemTool):
    name: str = READ_MULTIPLE_FILES_TOOL.name
    args_schema: type[BaseModel] = ReadMultipleFilesInput
    description: str = READ_MULTIPLE_FILES_TOOL.description

    def execute(self, paths: List[str]) -> str:
        results = []

        for file_path in paths:
            try:
                validated_path = self.validate_path(file_path)
                with open(validated_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                results.append(f"{file_path}:\n{content}\n")
            except Exception as e:
                results.append(f"{file_path}: Error - {str(e)}")

        return "\n---\n".join(results)


class WriteFileTool(BaseFilesystemTool):
    name: str = WRITE_FILE_TOOL.name
    args_schema: type[BaseModel] = WriteFileInput
    description: str = WRITE_FILE_TOOL.description

    def execute(self, path: str, content: str) -> str:
        validated_path = self.validate_path(path)
        try:
            os.makedirs(os.path.dirname(validated_path), exist_ok=True)

            with open(validated_path, 'w', encoding='utf-8') as file:
                file.write(content)

            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file {path}: {str(e)}"


class EditFileTool(BaseFilesystemTool):
    name: str = EDIT_FILE_TOOL.name
    args_schema: type[BaseModel] = EditFileInput
    description: str = EDIT_FILE_TOOL.description

    def normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to LF."""
        return text.replace('\r\n', '\n')

    def create_unified_diff(self, original_content: str, new_content: str, filepath: str = 'file') -> str:
        """Create a unified diff between original and new content."""
        normalized_original = self.normalize_line_endings(original_content)
        normalized_new = self.normalize_line_endings(new_content)

        diff_lines = list(difflib.unified_diff(
            normalized_original.splitlines(keepends=True),
            normalized_new.splitlines(keepends=True),
            fromfile=filepath,
            tofile=filepath,
            fromfiledate='original',
            tofiledate='modified'
        ))

        return ''.join(diff_lines)

    def _find_exact_match(self, old_lines: List[str], content_lines: List[str]) -> Optional[int]:
        """Find the exact match position for a set of lines in the content."""
        for i in range(len(content_lines) - len(old_lines) + 1):
            potential_match = content_lines[i:i + len(old_lines)]
            
            is_match = all(
                old_line.strip() == content_line.strip()
                for old_line, content_line in zip(old_lines, potential_match)
            )
            
            if is_match:
                return i
        return None
    
    def _get_indent(self, line: str) -> str:
        """Extract the indentation from a line."""
        indent_match = re.match(r'^\s*', line)
        return indent_match.group(0) if indent_match else ''
    
    def _format_new_line(self, line: str, j: int, original_indent: str, old_lines: List[str], new_lines_split: List[str]) -> str:
        """Format a new line with proper indentation."""
        if j == 0:
            return original_indent + line.lstrip()
        
        old_indent = self._get_indent(old_lines[j] if j < len(old_lines) else '')
        new_indent = self._get_indent(line)
        
        if old_indent and new_indent:
            relative_indent = max(0, len(new_indent) - len(old_indent))
            return original_indent + ' ' * relative_indent + line.lstrip()
        else:
            return line
    
    def _replace_lines_with_indentation(self, content_lines: List[str], match_index: int, old_lines: List[str], normalized_new: str) -> List[str]:
        """Replace lines while preserving indentation."""
        original_indent = self._get_indent(content_lines[match_index])
        new_lines = []
        
        for j, line in enumerate(normalized_new.split('\n')):
            new_lines.append(self._format_new_line(line, j, original_indent, old_lines, normalized_new.split('\n')))
        
        result = content_lines.copy()
        result[match_index:match_index + len(old_lines)] = new_lines
        return result
    
    def _format_diff_output(self, diff: str) -> str:
        """Format the diff output with appropriate backticks."""
        num_backticks = 3
        while '`' * num_backticks in diff:
            num_backticks += 1
        
        return f"{'`' * num_backticks}diff\n{diff}{'`' * num_backticks}\n\n"

    def apply_file_edits(
            self,
            file_path: str,
            edits: List[EditOperation],
            dry_run: bool = False
    ) -> str:
        """Apply edits to a file and return a diff."""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = self.normalize_line_endings(file.read())

        modified_content = content
        for edit in edits:
            normalized_old = self.normalize_line_endings(edit.old_text)
            normalized_new = self.normalize_line_endings(edit.new_text)

            # Simple case: direct string replacement
            if normalized_old in modified_content:
                modified_content = modified_content.replace(normalized_old, normalized_new)
                continue

            # More complex case: line-by-line matching with indentation preservation
            old_lines = normalized_old.split('\n')
            content_lines = modified_content.split('\n')
            
            match_index = self._find_exact_match(old_lines, content_lines)
            if match_index is not None:
                content_lines = self._replace_lines_with_indentation(
                    content_lines, match_index, old_lines, normalized_new
                )
                modified_content = '\n'.join(content_lines)
            else:
                raise ValueError(f"Could not find exact match for edit:\n{edit.old_text}")

        # Create and format the diff
        diff = self.create_unified_diff(content, modified_content, file_path)
        formatted_diff = self._format_diff_output(diff)

        # Write changes if not a dry run
        if not dry_run:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)

        return formatted_diff

    def execute(self, path: str, edits: List[EditOperation], dry_run: Optional[bool] = False) -> str:
        validated_path = self.validate_path(path)
        try:
            edit_operations = []
            for edit in edits:
                old_text = edit.old_text
                new_text = edit.new_text
                edit_operations.append(EditOperation(old_text=old_text, new_text=new_text))

            result = self.apply_file_edits(validated_path, edit_operations, dry_run)
            return result
        except Exception as e:
            return f"Error editing file {path}: {str(e)}"


class CreateDirectoryTool(BaseFilesystemTool):
    name: str = CREATE_DIRECTORY_TOOL.name
    args_schema: type[BaseModel] = CreateDirectoryInput
    description: str = CREATE_DIRECTORY_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            os.makedirs(validated_path, exist_ok=True)
            return f"Successfully created directory {path}"
        except Exception as e:
            return f"Error creating directory {path}: {str(e)}"


class ListDirectoryTool(BaseFilesystemTool):
    name: str = LIST_DIRECTORY_TOOL.name
    args_schema: type[BaseModel] = ListDirectoryInput
    description: str = LIST_DIRECTORY_TOOL.description

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)
        try:
            entries = []
            with os.scandir(validated_path) as it:
                for entry in it:
                    # Skip entries that match the ignore patterns
                    should_ignore = any(
                        fnmatch.fnmatch(entry.name, pattern) or
                        (pattern in entry.name and '*' not in pattern)
                        for pattern in DEFAULT_IGNORE_PATTERNS
                    )
                    if should_ignore:
                        continue
                        
                    prefix = "[DIR]" if entry.is_dir() else "[FILE]"
                    entries.append(f"{prefix}{entry.name}")

            return "\n".join(entries) if entries else "Empty directory"
        except Exception as e:
            return f"Error listing directory {path}: {str(e)}"


class DirectoryTreeTool(BaseFilesystemTool):
    name: str = DIRECTORY_TREE_TOOL.name
    args_schema: type[BaseModel] = DirectoryTreeInput
    description: str = DIRECTORY_TREE_TOOL.description

    def _should_ignore_entry(self, entry_name: str, relative_path: str) -> bool:
        """Check if an entry should be ignored based on patterns."""
        return any(
            fnmatch.fnmatch(entry_name, pattern) or 
            fnmatch.fnmatch(relative_path, pattern) or
            (pattern in relative_path and '*' not in pattern)
            for pattern in DEFAULT_IGNORE_PATTERNS
        )
    
    def _process_directory_entry(self, entry, current_path: str) -> Optional[Dict[str, Any]]:
        """Process a single directory entry for the tree."""
        try:
            relative_path = os.path.relpath(os.path.join(current_path, entry.name), current_path)
            
            if self._should_ignore_entry(entry.name, relative_path):
                return None
                
            entry_data = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file"
            }
            
            if entry.is_dir():
                children = self.build_tree(os.path.join(current_path, entry.name))
                entry_data["children"] = children
                
            return entry_data
            
        except Exception:
            return None

    def build_tree(self, current_path: str) -> List[Dict[str, Any]]:
        """Build a tree structure of files and directories."""
        try:
            validated_path = self.validate_path(current_path)
            result = []

            with os.scandir(validated_path) as it:
                for entry in it:
                    entry_data = self._process_directory_entry(entry, current_path)
                    if entry_data:
                        result.append(entry_data)

            return result
        except Exception as e:
            logger.error(f"Error building tree for {current_path}: {str(e)}")
            return []

    def execute(self, path: str) -> str:
        try:
            tree_data = self.build_tree(path)
            return json.dumps(tree_data, indent=2)
        except Exception as e:
            return f"Error generating directory tree for {path}: {str(e)}"


class MoveFileTool(BaseFilesystemTool):
    name: str = MOVE_FILE_TOOL.name
    args_schema: type[BaseModel] = MoveFileInput
    description: str = MOVE_FILE_TOOL.description

    def execute(self, source: str, destination: str) -> str:
        valid_source_path = self.validate_path(source)
        valid_dest_path = self.validate_path(destination)

        try:
            dest_dir = os.path.dirname(valid_dest_path)
            os.makedirs(dest_dir, exist_ok=True)

            shutil.move(valid_source_path, valid_dest_path)
            return f"Successfully moved {source} to {destination}"
        except Exception as e:
            return f"Error moving {source} to {destination}: {str(e)}"


class SearchFilesTool(BaseFilesystemTool):
    name: str = SEARCH_FILES_TOOL.name
    args_schema: type[BaseModel] = SearchFilesInput
    description: str = SEARCH_FILES_TOOL.description

    def _should_exclude_path(self, relative_path: str, exclude_patterns: List[str]) -> bool:
        """Check if a path should be excluded based on patterns."""
        return any(
            fnmatch.fnmatch(relative_path, excl_pattern if '*' in excl_pattern else f"**/{excl_pattern}/**")
            for excl_pattern in exclude_patterns
        )
    
    def _process_entry(self, entry, current_path: str, root_path: str, pattern: str, exclude_patterns: List[str], results: List[str]) -> None:
        """Process a single directory entry during search."""
        try:
            full_path = os.path.join(current_path, entry.name)
            self.validate_path(full_path)
            
            relative_path = os.path.relpath(full_path, root_path)
            
            if self._should_exclude_path(relative_path, exclude_patterns):
                return
                
            # Check if entry matches the search pattern
            if pattern.lower() in entry.name.lower():
                results.append(full_path)
                
            # Recursively search directories
            if entry.is_dir():
                self._search_directory(full_path, root_path, pattern, exclude_patterns, results)
                
        except Exception:
            # Skip entries that cause errors
            pass
    
    def _search_directory(self, current_path: str, root_path: str, pattern: str, exclude_patterns: List[str], results: List[str]) -> None:
        """Search a directory recursively for files matching the pattern."""
        try:
            with os.scandir(current_path) as it:
                for entry in it:
                    self._process_entry(entry, current_path, root_path, pattern, exclude_patterns, results)
        except Exception:
            # Skip directories that can't be accessed
            pass

    def search_files(
            self,
            root_path: str,
            pattern: str,
            exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """Search for files matching a pattern."""
        if exclude_patterns is None:
            exclude_patterns = []
            
        results = []
        self._search_directory(root_path, root_path, pattern, exclude_patterns, results)
        return results

    def execute(self, path: str, pattern: str, exclude_patterns: Optional[List[str]] = None) -> str:
        if exclude_patterns is None:
            exclude_patterns = []
            
        # Always include the default ignore patterns
        exclude_patterns = list(set(exclude_patterns + DEFAULT_IGNORE_PATTERNS))

        validated_path = self.validate_path(path)

        try:
            results = self.search_files(validated_path, pattern, exclude_patterns)
            return "\n".join(results) if results else "No matches found"
        except Exception as e:
            return f"Error searching in {path}: {str(e)}"


class GetFileInfoTool(BaseFilesystemTool):
    name: str = GET_FILE_INFO_TOOL.name
    args_schema: type[BaseModel] = GetFileInfoInput
    description: str = GET_FILE_INFO_TOOL.description

    def get_file_stats(self, file_path: str) -> Dict[str, Union[int, str, bool]]:
        """Get detailed file stats."""
        stats = os.stat(file_path)
        return {
            "size": stats.st_size,
            "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stats.st_atime).isoformat(),
            "isDirectory": os.path.isdir(file_path),
            "isFile": os.path.isfile(file_path),
            "permissions": oct(stats.st_mode & 0o777)[-3:]
        }

    def execute(self, path: str) -> str:
        validated_path = self.validate_path(path)

        try:
            info = self.get_file_stats(validated_path)
            return "\n".join(f"{key}: {value}" for key, value in info.items())
        except Exception as e:
            return f"Error getting file info for {path}: {str(e)}"


class ListAllowedDirectoriesTool(BaseFilesystemTool):
    name: str = LIST_ALLOWED_DIRECTORIES_TOOL.name
    args_schema: Optional[type[BaseModel]] = None
    description: str = LIST_ALLOWED_DIRECTORIES_TOOL.description

    def execute(self) -> str:
        if not self.filesystem_config or not self.filesystem_config.allowed_directories:
            return "No allowed directories configured"

        return f"Allowed directories:\n{os.linesep.join(self.filesystem_config.allowed_directories)}"


class CommandLineTool(BaseFilesystemTool):
    name: str = COMMAND_LINE_TOOL.name
    args_schema: type[BaseModel] = CommandLineInput
    description: str = COMMAND_LINE_TOOL.description
    timeout: int = 120  # Default timeout in seconds

    # Define dangerous patterns as a class variable to avoid recreating it each time
    _DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",  # Prevent removing root directory
        r"mkfs",  # Prevent formatting drives
        r"dd\s+if=",  # Prevent disk operations
        r"wget\s+.+\s+\|\.+sh",  # Prevent downloading and piping to shell
        r"curl\s+.+\s+\|\.+sh",  # Prevent downloading and piping to shell
        r"sudo",  # Prevent privilege escalation
        r"chmod\s+777",  # Prevent setting unsafe permissions
        r"chmod\s+\+x",  # Prevent making files executable
        r">\s*/etc/",  # Prevent writing to system config
        r">\s*/dev/",  # Prevent writing to devices
    ]
    
    def _contains_dangerous_pattern(self, command: str, pattern: str) -> bool:
        """Check if a command contains a specific dangerous pattern."""
        return bool(re.search(pattern, command, re.IGNORECASE))
    
    def _sanitize_command(self, command: str) -> Optional[str]:
        """Sanitize the command for security purposes.
        
        Returns an error message if the command is not allowed, None if it's safe.
        """
        for pattern in self._DANGEROUS_PATTERNS:
            if self._contains_dangerous_pattern(command, pattern):
                return f"Command contains potentially dangerous pattern: {pattern}"
        
        return None

    def execute(self, command: str, working_directory: Optional[str] = None) -> str:
        # Sanitize the command
        error = self._sanitize_command(command)
        if error:
            return f"Error: {error}"
        
        # Set working directory
        if working_directory:
            work_dir = self.validate_path(working_directory)
            if not os.path.isdir(work_dir):
                return f"Error: Working directory does not exist: {working_directory}"
        else:
            # Use the first allowed directory as default
            if self.filesystem_config and self.filesystem_config.allowed_directories:
                work_dir = self.validate_path(self.filesystem_config.allowed_directories[0])
            else:
                work_dir = os.getcwd()
        
        try:
            # Execute the command with timeout
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # Prepare the output
            output = [f"Working directory: {work_dir}"]
            output.append(f"Command: {command}")
            output.append(f"Exit code: {result.returncode}")
            
            if result.stdout:
                output.append("\nStandard output:")
                output.append(result.stdout)
            
            if result.returncode != 0 and result.stderr:
                output.append("\nStandard error:")
                output.append(result.stderr)
            
            return "\n".join(output)
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
