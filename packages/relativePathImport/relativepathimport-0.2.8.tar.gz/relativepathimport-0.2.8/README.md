
# Overview
The `relativePathImport` class provides various utilities to handle paths in a project and allows you to work with relative paths, navigate backwards in the directory structure, and import modules from relative file locations. It works for both windows and linux.

# getCurrentFilePath():
**Purpose:**  
Returns the absolute path of the current file in which the function is called.

**Description:**  
This function identifies the absolute path of the Python script from which it is invoked. It goes up the call stack, looking for the first frame that isn't part of the IPython interactive shell (if you're using Jupyter or IPython). It then executes a piece of code to capture the current file's path.

**Example:**  
`relativePathImport.getCurrentFilePath()`

*This will return the absolute file path of the script from which it is called.*

**Explanation:**  
- The function uses the Python `inspect` module to walk up the call stack and find the relevant frame.
- It executes code in the caller's context to retrieve the file path.

# relativeToAbsolute( relative_path ):
**Purpose:**  
Converts a relative file path to an absolute file path, based on the current file's location.

**Description:**  
This function takes a relative path and returns its absolute path. It works by figuring out the location of the current file and appending the relative path to it. If the relative path is just a filename (no directories), it assumes the file is in the same directory as the current script.

**Example:**  
```
relative_path = "folder/desiredFile.py"
absolute_path = relativePathImport.relativeToAbsolute(relative_path)
print(absolute_path)
```
*This will print the absolute path of `folder/desiredFile.py`, assuming the current file's directory is the base for the relative path.*

**Explanation:**  
- It breaks the relative path into directory components and the filename.
- It checks if the relative path has directories and attempts to resolve them based on the current file’s path.

**Going Back in Paths**  
The `relativeToAbsolute` function resolves relative paths, including navigating back (up) the directory structure using `..`. This allows you to move up multiple levels from the current directory and then continue to a specified file or folder.

**How It Works:**  
1. `..` represents moving up one directory.
2. The function combines the current directory with the relative path and resolves any `..` to compute the absolute path.

**Examples:**  
1. Moving Up One Directory:  
- Relative path: `../file.txt`
- Current directory: `/home/user/projects/folder1/folder2`
- Resulting absolute path: `/home/user/projects/folder1/file.txt`

2. Moving Up Two Directories:  
- Relative path: `../../file.txt`
- Current directory: `/home/user/projects/folder1/folder2`
- Resulting absolute path: `/home/user/projects/file.txt`

3. Moving Up Three Directories:  
- Relative path: `../../../file.txt`
- Current directory: `/home/user/projects/folder1/folder2/folder3`
- Resulting absolute path: `/home/user/file.txt`

4. Complex Path with Subfolders:  
- Relative path: `../../folder1/folder2/file.txt`
- Current directory: `/home/user/projects/folder1/folder2/folder3`
- Resulting absolute path: `/home/user/projects/folder1/folder2/file.txt`

This explains how `relativeToAbsolute` works with examples of navigating back (up) through directories using `..`.

# importFromRelativePath( relative_path , namee ):
**Purpose:**  
Imports a Python module from a file specified by a relative path.

**Description:**  
This function first resolves the absolute path of the Python file (using `relativeToAbsolute`), and then dynamically imports the module using `importlib`. It allows for importing modules that are not in the standard Python path.

**Example:**
```
module = relativePathImport.importFromRelativePath("folder/subfolder", "desiredModule")
```
*This will import the `desiredModule.py` file from `folder/subfolder`.*

**Explanation:**  
- `importlib` is used to import the module from a specific file path.
- It adds the module to `sys.modules`, which is how Python tracks all loaded modules.

*This should also work for paths that require going backwards just as explained in the docs for `relativeToAbsolute( relative_path )`*

# goBackwards( pathh ):
THIS FUNCTION IS NOT NECESSARY BECAUSE `relativeToAbsolute` ALREADY DOES THIS!
        
**Purpose:**  
Navigates "backwards" in a path by reducing it based on `..` (parent directory) references.

**Description:**  
This function reduces a given path by the number of `..` entries it contains. For example, `../../folder/file.py` will move up two levels in the directory structure. It also handles absolute paths and normalizes the path format.

**Example:**  
```
path = relativePathImport.goBackwards("../../folder/desiredFile.py")
print(path)
```
*This will return a normalized absolute path after moving up two levels from the current file.*

**Explanation:**  
- The function counts the number of `..` references in the path.
- It then uses `os.path.dirname` to traverse backwards from the current file’s directory.

**Detailed Explanation of `goBackwards()`**  
The `goBackwards()` function works by parsing the given relative path for `..` references, which indicate how many directories to go "up." Here's a step-by-step breakdown:
1. Split the path into components: The path is split using `os.sep`, which works for both `/` and `\` based on the operating system.
2. Count the `..` entries: For each `..`, the function knows it needs to go up one directory level.
3. Normalize the path: It builds a "backwards" path by reducing the number of directories based on the `..` count.
4. Combine the reduced path with the base path: It then combines this reduced path with the base path of the current file to get the final result.

**For Example:**  
If your file is located at `/home/user/projects/currentProject/script.py`, and you want to navigate to `../../../realFolderInPath/folderNotInPresentFilesPath/desiredFile.py`, here's what happens:

- `../../../` tells the function to go up three levels from the current directory (`/home/user/projects/currentProject/`).
- After going up three levels, it will be at `/home/user/`.
- Then it adds `realFolderInPath/folderNotInPresentFilesPath/desiredFile.py` to the path, resulting in `/home/user/realFolderInPath/folderNotInPresentFilesPath/desiredFile.py`.
