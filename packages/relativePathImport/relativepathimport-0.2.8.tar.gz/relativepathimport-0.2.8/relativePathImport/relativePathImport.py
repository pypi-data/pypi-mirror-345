
import os
import importlib
import sys
import inspect


class relativePathImport(): #importRelative():
    '''
    The `relativePathImport` class provides various utilities to handle paths in a project and allows you to work with relative paths, navigate backwards in the directory structure, and import modules from relative file locations. It works for both windows and linux.
    '''
    def getCurrentFilePath():
        '''
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
        '''
        def remove_leading_whitespace(text):
            # Split the text into lines
            lines = text.split('\n')

            # Find the minimum amount of leading whitespace
            min_whitespace = float('inf')
            for line in lines:
                stripped_line = line.lstrip()
                leading_whitespace = len(line) - len(stripped_line)
                if stripped_line:  # Ignore completely empty lines
                    min_whitespace = min(min_whitespace, leading_whitespace)

            # Subtract the minimum amount of leading whitespace from each line
            adjusted_lines = [line[min_whitespace:] for line in lines]

            # Join the lines back into a single string
            adjusted_text = '\n'.join(adjusted_lines)
            
            return adjusted_text
        
        code_to_run = remove_leading_whitespace( '''
            import os
            current_file_path_8286433374 = os.path.abspath(__file__)
            ''' )
        
        # print("finding file path")
        def canGoBack( framee ):
            def isIPythonCore( pathh ):
                # c:\Users\brigh\.conda\envs\selenium\Lib\site-packages\IPython\core\interactiveshell.py
                # inspection: c:\Users\brigh\.conda\envs\selenium\Lib\site-packages\IPython\core\interactiveshell.py
                # c:\Users\brigh\.conda\envs\selenium\Lib\site-packages\IPython\core\interactiveshell.py
                return "IPython\core" in pathh  ### ".conda\envs" in pathh or 
        
            frameBehind = framee.f_back
            if frameBehind:
                exec(code_to_run, frameBehind.f_globals, frameBehind.f_locals)
                # print("  - ", frameBehind.f_locals['current_file_path_8286433374'] )
                if isIPythonCore(   frameBehind.f_locals['current_file_path_8286433374']   ):
                    return False
                else:
                    return True            
            else:
                print("   reached end")
                return False
            
        caller_frame = inspect.currentframe()

        while  canGoBack( caller_frame ):
            caller_frame = caller_frame.f_back
        
        exec(code_to_run, caller_frame.f_globals, caller_frame.f_locals)

        return caller_frame.f_locals['current_file_path_8286433374']

    def relativeToAbsolute( relative_path ):
        '''
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
        '''
        # p#rint("test_getCurrentFilePath():", relativePathImport.getCurrentFilePath())
        
        def getRelativePathList( relative_path ):
            relative_path_2 = os.path.normpath(relative_path)
            folders = relative_path_2.split(os.path.sep)
            return folders[0:-1], folders[-1]
        folderList, namee = getRelativePathList( relative_path )
        
        if len(folderList) == 0:
            # base_path = os.path.normpath( os.getcwd() + "\\" + namee )
            # base_path = os.path.normpath( os.path.dirname( relativePathImport.getCurrentFilePath() ) + "\\" + namee )
            base_path = os.path.normpath( os.path.join( os.path.dirname( relativePathImport.getCurrentFilePath() ) , namee ))
            
            return base_path
        
        def getBasePathList():
            # base_path = os.getcwd()
            base_path = relativePathImport.getCurrentFilePath()
            
            #p#rint("  getBasePathList - base_path:", base_path)
            if False: # yes, this does technically work, but no i want a more elegant solution
                folders = []
                while True:
                    base_path, folder = os.path.split(base_path)
                    if folder:
                        folders.insert(0, folder)  # Insert at the beginning to maintain order
                    else:
                        break
                return folders
            
            relative_path_2 = os.path.normpath( base_path )
            folders = relative_path_2.split(os.path.sep)
            return folders[0:-1]
        
        baseFolders = getBasePathList()

       

        baseFolders_special = "_|_".join( baseFolders )
        # p#rint("  baseFolders_special:" , baseFolders_special )
        # p#rint("   folderList_joined:", "_|_".join(folderList) )
        
        def find_sublist_start(large_list, sub_list):
            sub_len = len(sub_list)
            
            # large_list = [1,2,3,4,5,6]
            # sub_len = 2
            # print(list(range(len(large_list) - sub_len + 1)))
            # print(list(range(len(large_list) - sub_len , -1, -1)))
            # for i in range(len(large_list) - sub_len + 1):
            
            for i in range(len(large_list) - sub_len , -1, -1):
                if large_list[i:i + sub_len] == sub_list:
                    return i
            return -1  # R

        preSubPath = -1
        for i in range( len(folderList),0,-1 ):
            folderList_special = "_|_".join( folderList[:i] )
            if folderList_special in baseFolders_special:
                startOfSubPath = find_sublist_start(
                                    large_list = baseFolders, 
                                    sub_list = folderList[:i] )
                preSubPath = baseFolders[:startOfSubPath]
                break
        
        if preSubPath == -1:
            # current_file_path = os.path.abspath(__file__)
            # print("Path to the current file:", current_file_path)
            # assert preSubPath != -1
            
            # base_path = os.path.normpath( os.path.dirname( relativePathImport.getCurrentFilePath() ) + "\\" + relative_path )
            base_path = os.path.normpath(os.path.join( os.path.dirname( relativePathImport.getCurrentFilePath() ) , relative_path ))
            
            
            return base_path

        theWholePathList = preSubPath + folderList + [namee] # had ["C:"] at the start
        actualPath = "/".join( theWholePathList )
        return actualPath

    def importFromRelativePath( relative_path , namee ):
        '''
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
        '''

        abs_path = relativePathImport.relativeToAbsolute( relative_path )

        def import_module_from_path(file_path, module_name):
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

        return import_module_from_path(abs_path , namee )

    ####### NOT NECESSARY, relativeToAbsolute already does this #######
    def goBackwards( pathh ):
        '''
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
        '''

        # example path (this one is not valid)
        # pathh = "../../openDental/notWork/multi_seach_engine/top_million_sites.csv"
        if False:
            pathh = "../notWork/multi_seach_engine/top_million_sites.csv"
        normalized_path = os.path.normpath(pathh)  # This will handle both \ and /
        
        components = normalized_path.split(os.sep)
        
        backward_count = components.count("..")

        def getReducedPath():
            stack = []
            
            for component in components:
                if component == '..':
                    if stack:
                        stack.pop()  # Go one directory back (pop the last valid directory)
                elif component and component != '.':
                    stack.append(component)  # Add valid directories or files
            
            # Rebuild the path without '..'
            return os.sep.join(stack)
        reducedPath = getReducedPath()

        def goBackwardsFromPresentPath( backward_count ):
            startPath = os.path.dirname( relativePathImport.getCurrentFilePath() )

            for i in range( backward_count ):
                startPath = os.path.dirname( startPath )

            return startPath
        backwardsFromPresentPath = goBackwardsFromPresentPath( backward_count )
        
        combinedPaths = os.path.normpath(backwardsFromPresentPath + "/" + reducedPath)
        
        return combinedPaths
