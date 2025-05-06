from cli.coding.models import ToolMetadata

# Default patterns to ignore in directory operations
DEFAULT_IGNORE_PATTERNS = [
    'node_modules',
    'dist',
    'build',
    '.git',
    '.vscode',
    '.idea',
    'coverage',
    '*.min.js',
    '*.bundle.js',
    '*.map'
]

READ_FILE_TOOL = ToolMetadata(
    name="read_file",
    description="Read the complete contents of a file from the file system. "
                "Handles various text encodings and provides detailed error messages "
                "if the file cannot be read. Use this tool when you need to examine "
                "the contents of a single file. Only works within allowed directories.",
    label="Read File",
)

READ_MULTIPLE_FILES_TOOL = ToolMetadata(
    name="read_multiple_files",
    description="Read the contents of multiple files simultaneously. This is more "
                "efficient than reading files one by one when you need to analyze "
                "or compare multiple files. Each file's content is returned with its "
                "path as a reference. Failed reads for individual files won't stop "
                "the entire operation. Only works within allowed directories.",
    label="Read Multiple Files",
)

WRITE_FILE_TOOL = ToolMetadata(
    name="write_file",
    description="Create a new file or completely overwrite an existing file with new content. "
                "Use with caution as it will overwrite existing files without warning. "
                "Handles text content with proper encoding. Only works within allowed directories.",
    label="Write File",
)

EDIT_FILE_TOOL = ToolMetadata(
    name="edit_file",
    description="Make line-based edits to a text file. Each edit replaces exact line sequences "
                "with new content. Returns a git-style diff showing the changes made. "
                "Only works within allowed directories.",
    label="Edit File",
)

CREATE_DIRECTORY_TOOL = ToolMetadata(
    name="create_directory",
    description="Create a new directory or ensure a directory exists. Can create multiple "
                "nested directories in one operation. If the directory already exists, "
                "this operation will succeed silently. Perfect for setting up directory "
                "structures for projects or ensuring required paths exist. Only works within allowed directories.",
    label="Create Directory",
)

LIST_DIRECTORY_TOOL = ToolMetadata(
    name="list_directory",
    description="Get a detailed listing of all files and directories in a specified path. "
                "Results clearly distinguish between files and directories with [FILE] and [DIR] "
                "prefixes. Common directories and files like node_modules, .git, etc. are automatically "
                "excluded from results. This tool is essential for understanding directory structure and "
                "finding specific files within a directory. Only works within allowed directories.",
    label="List Directory",
)

DIRECTORY_TREE_TOOL = ToolMetadata(
    name="directory_tree",
    description="Get a recursive tree view of files and directories as a JSON structure. "
                "Each entry includes 'name', 'type' (file/directory), and 'children' for directories. "
                "Files have no children array, while directories always have a children array (which may be empty). "
                "Common directories and files like node_modules, .git, etc. are automatically excluded from results. "
                "The output is formatted with 2-space indentation for readability. Only works within allowed directories.",
    label="Directory Tree",
)

MOVE_FILE_TOOL = ToolMetadata(
    name="move_file",
    description="Move or rename files and directories. Can move files between directories "
                "and rename them in a single operation. If the destination exists, the "
                "operation will fail. Works across different directories and can be used "
                "for simple renaming within the same directory. Both source and destination must be within allowed directories.",
    label="Move File",
)

SEARCH_FILES_TOOL = ToolMetadata(
    name="search_files",
    description="Recursively search for files and directories matching a pattern. "
                "Searches through all subdirectories from the starting path. The search "
                "is case-insensitive and matches partial names. Returns full paths to all "
                "matching items. Common directories and files like node_modules, .git, etc. are automatically "
                "excluded from results. Great for finding files when you don't know their exact location. "
                "Only searches within allowed directories.",
    label="Search Files",
)

GET_FILE_INFO_TOOL = ToolMetadata(
    name="get_file_info",
    description="Retrieve detailed metadata about a file or directory. Returns comprehensive "
                "information including size, creation time, last modified time, permissions, "
                "and type. This tool is perfect for understanding file characteristics "
                "without reading the actual content. Only works within allowed directories.",
    label="Get File Info",
)

LIST_ALLOWED_DIRECTORIES_TOOL = ToolMetadata(
    name="list_allowed_directories",
    description="Returns the list of directories that this server is allowed to access. "
                "Use this to understand which directories are available before trying to access files.",
    label="List Allowed Directories",
)

COMMAND_LINE_TOOL = ToolMetadata(
    name="command_line",
    description="Execute shell commands in the operating system. This tool allows running "
                "commands like 'ls', 'grep', or any other available shell command. "
                "Use with caution as it executes commands with the same permissions as the "
                "running application. Only works within allowed directories.",
    label="Command Line",
)
