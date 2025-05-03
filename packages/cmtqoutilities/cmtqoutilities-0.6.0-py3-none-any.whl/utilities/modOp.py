import numpy as np
import datetime
import time
import subprocess
import platform
from pathlib import Path
from shutil import move,copy2,copytree,rmtree
from nbconvert import ScriptExporter
from nbformat import read

import utilities.database as database


operatingSystem=platform.system()

class Operator():
    """ Class to run experiments
    
    The modOp infrastructure helps in running experiments in the cmtqo lab. The idea is to develop the experiments in iptyhon notebooks using an IDE like Visual Studio Code or similar. The actual experiment is then initated from the notebook but the modOp spawns a process run in the background. It takes care of moving all needed code to a sandboxed environment and runs the experimnent from the command line using this sandboxed code in a well defined virtual environment. The data is stored according to a file structure reflecting setup, date and a unqiue ID (called `mid`). This mid along with a defined number of metadata fields are stored in an SQL database which is then also used for data retrieval. The workflow is as follows
     
    1.) Develop the code for the experiment in a notebook
    2.) Run the experiment using the modop, write down the mid in the labbook or the analysis notebook
    3.) Load the data using the mid and do the post processing in a suitable notebook. 

    Parameters
    ==========
    setupname : str
        name of the setup, has to exist in the SQL database
    datapath : str
        local location of the data. Within this directory a hirarachy setupName/YYYY-MM-DD/mid is created
        It is in the reponsablity of the operator to make sure this local data directory is periodically synced
        to the group drive
    codepath : str
        path to the notebook which is used for development
    libs : list[ str ]
        a list of locations from which custom libararies should be imported. These are copied to the data
        directory such that the experiment can be run from a sandboxed environment
    databaseDetails : dict
        dict containing the metadata for the SQL database
    vens : str
        location of the venv to be used. If None is given, $HOME/.ve/modop is assumed.     
    
    """
    
    def __init__(self,setupname=None,datapath=None,codepath=None,libs=[],databaseDetials=None,venv=None):
        
        # saves the ID (unique identifier) of the last experiment started
        self.currentID = None
        
        # the absolute path to the data is storage
        if datapath is None:
            if operatingSystem == 'Windows':
                self.dataPath = Path("D:/data")
            else:
                self.dataPath = Path.home() / "data"
        else:
            self.dataPath = Path(datapath)
        
        # the absolute path where the code resides
        if codepath is None:
            self.codePath=Path.home() / "code"
        else:
            self.codePath = Path(codepath)
        
        # create database handler
        if databaseDetials==None:
            self.db = database.Database()
        else:
            self.db = database.Database(databaseDetails=databaseDetials,datapath=datapath)
        
        # Force a setup name
        if setupname in self.db.properties['setups'] or setupname == 'Rogue':
            self.setupName=setupname
        else:
            print("You need to provide a setup name choose from:")
            for setup in self.db.properties['setups']:
                print("\t"+setup)
            print ("\n\nIf yout setup is new, add it to the database")
            raise Exception()
        
        # Check of libararies that we copy. 
        # This part should be largely deprecated as we 
        # hope to install all libraries via pip into a venv
        # But maybe some local libraries are still useful 
        # at times?
        self.userDefinedLibraryDirs=[]
        if len(libs)==0:
            print("You are not copying any libraries. Are you sure about that?")
        else:
            for library in libs:
                self.userDefinedLibraryDirs.append(Path(library))

        # Check if a venv is provided 
        if venv is not None:
            self.venv = Path(venv)
        else:
            self.venv = Path.home() / ".ve/modop"
        
        
        # Used to trim the juptyer file
        self.excludeMarker = ">>>>>"
        self.includeMarker = "<<<<<"
        self.lineIgnoreKeys = ["get_ipython().",".runExperiment("]
        
        
    
    
    
    def runExperiment(self,nbPath,databaseEntries):
        """
        Run the experiment:
        
            1. Generates a unique identifier for the measurement. 
            2. Generates a database entry. 
            3. Creates the file structure in the self.dataPath folder. 
            4. Creates a python file from the specified file in nbPath. 
            5. Copies all its dependencies into the created folders. 
            6. Opens a terminal window ready to running the script
        
        Prints information 
            - on which script it runs,
            - whether the database entry test flag is set,
            - the directory of the current measurement.
        
        Note that if the test flag in the database entries is set to true, the data will be 
        deleted from the database at some point.
        
        Parameters
        ==========
        
        nbPath: string
           File path of the notebook to be executed. Path is relative to self.codePath 
                            (e.g. "vibrometer/scripts/quadrupole/scan1D").
        
        databaseEntries: dict
          Dictionary specifying the database entries. Required keys are defined in self.db.reqDatabaseKeys.
        
                
        """
        # check for completeness of the databaseEntries
        if not self.db.isComplete(databaseEntries):
            return None
        
        # check appropriate file ending of the specified noteobok 
        if not nbPath.endswith(".ipynb"):
            self.currentNbPath = Path(nbPath + ".ipynb")
        else:
            self.currentNbPath = Path(nbPath)
        print("  \033[43m%s\033[0m"%self.currentNbPath)

        # check test flag and inform the user about the choice made
        if databaseEntries['test']:
            print("in test mode")
            print("  all your data will be \033[41m deleted \033[0m!")
        
        # Create the file strucutre
        self.createFileStructure()
        print("The directory is %s"%self.currentFoldername)
        
        # Export all code into it
        self.exportCode()
        
        # Create database entry
        success = self.db.createMeasurementEntry(self.currentID,
                                                 self.now,
                                                 self.currentFoldernameForDB,databaseEntries)
        if success:
            self.startExperiment()
        else:
            rmtree(self.currentFoldername, ignore_errors=True)
            print("Could not generate database entry. Did not start experiment.")

        return self.currentID, self.currentFoldername
    
    def createFileStructure(self):
        """
        Creates the file structure in the target directory of the experiment.
        
        The foldername structure is
        self.dataPath/self.setupName/date/uniqueIdentifier 
        
        """
        
        # created a unique identifier for the current run of the experiment
        self.createIdentifier()
        
        # create foldername
        self.now = datetime.datetime.now()
        self.nowString="%04i-%02i-%02i"%(self.now.year,self.now.month,self.now.day)

        self.currentFoldername = self.dataPath / self.setupName / self.nowString / self.currentID
        self.currentFoldernameForDB = Path(*self.currentFoldername.parts[-3:]).as_posix()

        self.currentFoldername.mkdir(parents=True, exist_ok=True)

        modules_folder = self.currentFoldername / "modules"

        # Create the modules folder and __init__.py
        if not modules_folder.exists():
            modules_folder.mkdir(parents=True)
            (modules_folder / "__init__.py").touch()

        # Now handle user-defined directories
        for directory in self.userDefinedLibraryDirs:
            tempSubFolder = modules_folder
            for part in directory.parts:
                tempSubFolder = tempSubFolder / part
                if not tempSubFolder.exists():
                    tempSubFolder.mkdir()
                    (tempSubFolder / "__init__.py").touch()
    
    def exportCode(self):
        """
        Export code into folder structure of current run. 
        
        """
        nbName = self.currentNbPath.stem
        #nbName = self.currentNbPath.split("/")[-1].split(".")[0]
        print(nbName)
        print(self.codePath / self.currentNbPath)

        #venv_path = Path(self.venv).resolve()

        # Use platform-native Python binary inside the venv
        # if platform.system() == "Windows":
        #     python_binary = venv_path / "Scripts" / "python.exe"
        # else:
        #     python_binary = venv_path / "bin" / "python"
        
        # create script
        #cmd=str(python_binary)+" -m nbconvert --to script "+str(self.codePath / self.currentNbPath)
        #print(cmd)
        #os.system(cmd)
        with open(self.codePath / self.currentNbPath) as f:
            nb = read(f, as_version=4)
        exporter = ScriptExporter()
        script, _ = exporter.from_notebook_node(nb)
        with open(nbName+".py", "w") as f:
            f.write(script)

        # adjust script
        f = open(nbName+".py",'r+')
        lines = f.readlines()
        include = True
        fromFuture = True
        importStarted = False
        for k, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                importStarted = True
            # check whether we are still in the from __future__ phase (from __future__ statements have to be at the very beginning of the code).
            if importStarted and not line.startswith("from __future__") and fromFuture:
                fromFuture = False
                # load os library as the first library after any from __future__ directive.
                # change into the correct working directory before any other import statements, such that the relative paths are correct.
                lines.insert(k,"os.chdir(r'%s')\n"%self.currentFoldername)
                lines.insert(k,"import os\n")
            # check whether line is suposed to be part of the code or not
            if self.excludeMarker in line:
                include = False
                lines[k] = '#'+line
                continue
            if self.includeMarker in line:
                include = True
                lines[k] = '#'+line
                continue
            if include:
                # comment lines matching self.lineIgnoreKeys
                for lineIgnoreKey in self.lineIgnoreKeys:
                    if lineIgnoreKey in line:
                        lines[k] = "# "+line
            else:
                # comment lines not to be included
                lines[k] = '#'+line
        # create standardized end of file
        lines.append('print("")\n')
        lines.append('print("")\n')
        lines.append('print("")\n')
        lines.append('print("****************************")\n')
        lines.append('print("Made it to the end of run.py")\n')
        f.seek(0)
        f.writelines(lines)
        f.close()
        
        # move script
        src = Path(f"{nbName}.py")
        dst = self.currentFoldername / "run.py"
        move(src, dst)

        
        # copy all the import files
        for directory in self.userDefinedLibraryDirs:
            src = self.codePath / directory
            dst = self.currentFoldername / "modules" / directory

            # Create the destination folder if it doesn't exist
            dst.mkdir(parents=True, exist_ok=True)

            # Copy contents of src into dst (but not the top-level src folder itself)
            for item in src.iterdir():
                target = dst / item.name
                if item.is_dir():
                    copytree(item, target, dirs_exist_ok=True)
                else:
                    copy2(item, target)
        
        # Find all Python files recursively in the current folder
        matches = list(self.currentFoldername.rglob("*.py"))

        # Replace import paths in all matched files
        for filepath in matches:
            content = filepath.read_text()

            for directory in self.userDefinedLibraryDirs:
                # directory is already a Path object
                libPath = ".".join(directory.parts)

                # Replace import statements
                content = content.replace(f"from {libPath}", f"from modules.{libPath}")
                content = content.replace(f"import {libPath}", f"import modules.{libPath}")

            # Replace code path references with modules path
            content = content.replace(str(self.codePath), str(self.currentFoldername / "modules"))

            filepath.write_text(content)
        return
    
    def startExperiment(self):
        """
        Starts the experiment using the Python binary from the venv.
        Do not call this method directly. Use runExperiment() instead.
        """

        current_id = self.currentID
        current_dir = Path(self.currentFoldername).resolve()
        venv_path = Path(self.venv).resolve()

        # Use platform-native Python binary inside the venv
        if platform.system() == "Windows":
            python_binary = venv_path / "Scripts" / "python.exe"
            pip_binary = venv_path / "Scripts" / "pip.exe"
        else:
            python_binary = venv_path / "bin" / "python"
            pip_binary = venv_path / "bin" / "pip"

        # Ensure path is a string for scripting
        python_binary = str(python_binary)
        pip_binary = str(pip_binary)
        current_dir_str = str(current_dir)


        system = platform.system()

        if system == "Darwin":
            # macOS: iTerm2 AppleScript using direct venv Python binary
            script = f'''
            tell application "iTerm2"
                set newWindow to (create window with default profile)
                tell current session of newWindow
                    set name to "Running MID: {current_id}"
                    set rows to 30
                    split horizontally with default profile
                end tell

                tell first session of current tab of newWindow
                    write text "cd {current_dir_str}"
                    write text "clear"
                    write text "pwd"
                    write text "{pip_binary} freeze > requirements.txt"
                    write text "{python_binary} -u run.py > run.log"
                end tell
                tell second session of current tab of current window
                    write text "cd {current_dir_str}"
                    write text "while [ ! -f run.log ]; do sleep 0.2; done"
                    write text "tail -f run.log"
                end tell
                activate
            end tell
            '''

            p = subprocess.Popen(['osascript', '-'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
            stdout, stderr = p.communicate(script.encode())

            if stderr:
                print("Error starting iTerm2:", stderr.decode())

        elif system == "Windows":
            # Windows: PowerShell script using direct venv Python binary
            powershell_script = f'''
            $processInfo = New-Object System.Diagnostics.ProcessStartInfo
            $processInfo.FileName = "powershell.exe"
            $processInfo.Arguments = "cd '{current_dir_str}'; {python_binary} -u run.py | Tee-Object -FilePath run.log; Read-Host 'Script ended, press Enter to exit...'"
            $processInfo.CreateNoWindow = $false
            $processInfo.UseShellExecute = $true
            [System.Diagnostics.Process]::Start($processInfo)
            '''

            script_path = Path("powershell_script.ps1").resolve()
            script_path.write_text(powershell_script)

            subprocess.run([
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ])

            time.sleep(5)
            script_path.unlink()

        else:
            raise NotImplementedError(f"startExperiment() is not supported on {system}")
    
    def createIdentifier(self):
        """
        Create a unique identifier for the current run of the experiment.
        
        Creates random identifier and checks with database that it is unique.
        Repeats until uniques is achieved.
        
        """
        # boolean whether generated identifier is unique
        newID = False
        success = True
        while(not newID):
            # create random integer
            num=np.random.randint(1,62**5)
            # choose number system with base 62
            base = 62
            identifier = ''
            k = 0
            # basis for number system
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            # rewrite num with respect to base 62
            while num > 0:
                rest = np.mod(num,base)
                num  = (num-rest)/base
                identifier = digits[int(rest)]+identifier
                k += 1
            # zero padding
            for n in range(k,5):
                identifier = '0'+identifier
            
            # check that the identifier is unused
            # create sql request
            sql = "SELECT mid FROM measurements"
            [success,dbSamples] = self.db.executeSqlRequest(sql)
            if success:
                # check for uniqueness
                newID = identifier not in dbSamples
            else:
                print("Could not access database to check for uniqueness of identifier. Set identifier to non-unique identifier '00000'.")
        if newID:
            self.currentID = identifier