# Foldora - File & Directory Manager CLI Tool

**Foldora** is a Python command-line interface (CLI) tool designed to help you efficiently manage files and directories.

## 🚀 Features

Foldora provides essential file and directory operations, including:

- 📝 Displaying file contents
- 🧹 Purging files and directories
- 📁 Listing files and directories  
- 📂 Creating directories and files  
- ✏️ Replacing spaces in file and directory names with underscores  

## 🛠️ Installation

To install Foldora, clone the repository and navigate to the project directory:

- PS: Make sure python is installed in case you're new to Python.

```sh
pip install foldora
```

## 📦 Usage

Run Foldora using the `fd` command followed by the desired operation.

### 📁 List Files and Directories

Lists all files and directories in the current or specified paths.

**Command:**

```sh
fd l [optional_paths]
```

**Examples:**

- List contents of the current directory

```sh
fd l
```

- List contents of specific directories

```sh
fd l /path/to/dir1 /path/to/dir2  
```

### 📂 Create Directories

Creates one or more directories.

**Command:**

```sh
fd d [paths]
```

**Example:**

```sh
fd d /path/to/dir1 /path/to/dir2 ...
```

### 📄 Create Files

Creates one or more files in the current directory or a specified path.

**Command:**

```sh
fd f '[-p path]' [file_paths]
```

**Examples:**

- Create files in the current directory

```sh
fd f file1.txt file2.txt  
```

- Create files in a specified directory

```sh
fd f -p /path/to/dir file1.txt file2.txt  
```

### 🧹 Purge Files and Directories

Deletes specified files and directories with user confirmation.

**Command:**

```sh
fd p [file_paths] [dir_paths]
```

**Example:**

```sh
fd p /path/to/dir1 /path/to/file1 ...
```

### 📝 Display File Contents

Shows the content of one or more files.

**Command:**

```sh
fd c [file_paths]
```

**Example:**

```sh
fd c /path/to/file1 /path/to/file2 ...
```

### ✏️ Fill Blanks in File/Directory Names

Replaces spaces in file and directory names within a given path with underscores.

If no path is provided, the current working directory is used. You will also be prompted to activate "Sub Filling" mode, which triggers a low-level operation.

**Command:**

```sh
fd b [path]
```

**Example:**

- Current directory

```sh
fd b
```

- Specific directory

```sh
fd b /path/to/dir
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve Foldora.

## 📄 License

This project is licensed under the MIT License.
