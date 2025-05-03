import numpy as np
try:
    import pymysql as MySQLdb
    withDB=True
except:
    withDB=False
import glob
import utilities.pythonArchive.garchive as garchive
import datetime
import os
from pathlib import Path
from shutil import copytree

class Database():
    def __init__(self,databaseDetails = {'host':"127.0.0.1", 'user':"klaus",'db':"data",'port':3306},
                      dbi=None,noDB=False,
                      datapath=None):
        if datapath is None:
            self.datapath=Path.home() / "data"
        else:
            self.datapath=Path(datapath)
        withDB=True
        if noDB:
            withDB = False
        if dbi is not None:
            withDB=dbi
        if withDB:
            with open(Path.home() / ".passwd", 'r') as myfile:
                databaseDetails['passwd']=myfile.read().replace('\n', '')
            self.withDB=True
            self.databaseDetails = databaseDetails
            self.connectDatabase()
            self.readDatabaseParameters()
            # these are the keys we need to provide in a dictionary handed over to the database -- otherwise the program will abort
            self.reqDatabaseKeys = ['operator','setup','type','intention','comment','sample','project','test']
        else:
            self.withDB=False
            print("You cannot load from DB, only Database.loadData() is available")
        
    
    def __delete__(self):
        if withDB:
            self.db.close()
        
    def connectDatabase(self):
        """
        Establish connection to database. Prints info in case it didn't work.
        
        Parameters
        ==========
        
        --- 
        
        Returns
        =======
        
        ---
        
        """
        self.databaseConnected = False
        try:
            self.db = MySQLdb.connect(host = self.databaseDetails['host'],
                                      port = self.databaseDetails['port'],
                                      user = self.databaseDetails['user'],
                                      passwd = self.databaseDetails['passwd'],
                                      db = self.databaseDetails['db'])
            self.dbCur = self.db.cursor()
            self.databaseConnected = True
        except Exception as e:
            print("Could not connect to database")
            print(e)
                
    def readDatabaseParameters(self):
        """
        Read the predefined database entries from the database and save them in self.properties.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        totSuccess = True
        self.properties = {}
        for keys in [['projects','title','projectid'],['setups','title','setupid'],['samples','name','sampleid'],
                     ['types','title','typeid'],['publications','title','publicationid']]:
            self.properties[keys[0]] = {}
            sql = "SELECT "+keys[1]+", "+keys[2]+" FROM "+keys[0]
            [success,dbSamples] = self.executeSqlRequest(sql)
            totSuccess = totSuccess and success
            if success:
                for k in range(dbSamples.shape[0]):
                    self.properties[keys[0]][dbSamples[k,0]] = dbSamples[k,1].astype(int)
        if not totSuccess:
            print("Could not read database parameters")
    
    def fetchData(self,mid=None):
        """
        Fetch data which got stored by a previously calling runExperiment (method of the mother class).
        
        Parameters
        ==========
        
        mid: string
          Unique measurement identifier. Check out the output of runExperiment or the database to find it. 
        
        Returns
        =======
        
        [garchivs]:
          List of garchive instances. Each instance corresponds to a file saved in the data folder of the measurement mid.
        
        """
        # Check database to find the location of a given measurement
        sql = "SELECT * FROM measurements ORDER BY date DESC LIMIT 1"
        if not mid == None:
            sql = "SELECT * FROM measurements WHERE mid = '%s'"%mid
        [success,dbSamples] = self.executeSqlRequest(sql)
        # remember current directory
        cwd = os.getcwd()
        # switch to directory cotaining the desired data
        os.chdir(self.datapath / dbSamples[0][3])
        # load data into garchives
        archs = []
        filenames = sorted((Path("data")).glob("*.npz"))
        for filename in filenames:
            ar = garchive.garchive()
            ar.load('./data',Path(filename).name)
            archs.append(ar)
        # change back into the previous working directory
        os.chdir(cwd)
        print("Loaded data from measurement "+dbSamples[0][0])
        return archs
        
        
    def loadData(self,dir):
        """
        Fetch data which got stored by a previously calling runExperiment (method of the mother class).
        
        Parameters
        ==========
        
        dir: string
          Directory from which to read garchives
        
        Returns
        =======
        
        [garchivs]:
          List of garchive instances. Each instance corresponds to a file saved in the data folder of the measurement mid.
        
        """
        # remember current directory
        cwd = os.getcwd()
        # switch to directory cotaining the desired data
        os.chdir(dir)
        # load data into garchives
        archs = []
        filenames = sorted((Path("data")).glob("*.npz"))
        for filename in filenames:
            ar = garchive.garchive()
            ar.load('./data',Path(filename).name)
            archs.append(ar)
        # change back into the previous working directory
        os.chdir(cwd)
        print("Loaded data from measurement")
        return archs
        
    def currentMID(self):
        sql = "SELECT mid FROM measurements ORDER BY date DESC LIMIT 1"
        [success,test]=self.executeSqlRequest(sql)
        return test[0][0]
        
        
    def exportData(self,mid=None,target=None):
        """
        Fetch data which got stored by a previously calling runExperiment (method of the mother class).
        
        Parameters
        ==========
        
        mid: string
          Unique measurement identifier. Check out the output of runExperiment or the database to find it. 
        
        Returns
        =======
        
        [garchivs]:
          List of garchive instances. Each instance corresponds to a file saved in the data folder of the measurement mid.
        
        """
        if target is None:
            target=Path.home() / "Desktop"
        # Check database to find the location of a given measurement
        sql = "SELECT * FROM measurements ORDER BY date DESC LIMIT 1"
        if not mid == None:
            sql = "SELECT * FROM measurements WHERE mid = '%s'"%mid
        [success,dbSamples] = self.executeSqlRequest(sql)
        
        # cmd='rsync -av '+self.datapath+'/'+dbSamples[0][3]+ ' '+target
        # print(cmd)
        # os.system(cmd)
        copytree(self.datapath / dbSamples[0][3], Path(target), dirs_exist_ok=True)
        return 0
    
    def executeSqlRequest(self,sql,fetch=True):
        """
        Execute an arbitrary sql request.
        
        Parameters
        ==========
        
        sql: string
          Sql request.
        
        fetch: bool
          If True, the sql request involves fetching data and the method will return them. If false no data fetching is involved.
        
        Returns
        =======
        
        [success, dbSamples]: [bool,np.array (objects)]
          success: flag whether the command was exectued successfully. 
          dbSamples: np.array with the querry results. If not success, it is an empty array.
        
        """
        success = True
        try:
            self.dbCur.execute(sql)
            self.db.commit()
            if fetch:
                dbSamples = np.array(self.dbCur.fetchall())
            else:
                dbSamples = None
        except:
            success = False
            self.db.rollback()
            dbSamples = np.array([])
            print("Database handler: request '%s' failed"%sql)
        return [success,dbSamples]
    
    def findMeasurement(self,
                        startDate=None,endDate=None,test=[],
                        setups=[],samples=[],projects=[],types=[],publications=[],
                        operatorContains=[],intentionContains=[],commentContains=[]):
        """
        Search the database for measurements matching the specified contitions. Different
        conditions are AND connected while multiple arguments for a given input parameter
        are OR connected.
        
        StartDate and endDate set the timeframe in which is searched. 
        
        All other input parameters are specified as lists. For every parameter, we search for 
        measurements satisfying at least one criterion in the corresponding list. 
        
        For setup, samples, projects, types, and publications the match has to be exact.
        For operatorContains, intentionContains, and commentContains the string specified as list
        element has to be contained in the corresponding field. The search is not case sensitive.
        
        If input parameters are not specified, the criterion is ignored. 
        
        
        Parameters
        ==========
        
        startDate: datetime.datetime
          Measurements has to be younger than startDate. Default value is 1.1.2000.
        
        endDate: datetime.datetime
          Measurements has to be older than startDate. Default value is datetime.now().
        
        test: bool
          If specified, check for test flag in measurement table.
        
        setups: list
          List with setup identifiers or setup names (can be mixed). For available values check self.setups.
        
        samples: list
          List with sample identifiers or sample names (can be mixed). For available values check self.samples.
        
        projects: list
          List with project identifiers or project names (can be mixed). For available values check self.projects.
        
        types: list
          List with type identifiers or type names (can be mixed). For available values check self.types.
        
        operatorContains: list
          List with strings to be looked for in the operator field.
        
        intentionContains: list
          List with strings to be looked for in the intention field.
        
        commentContains: list
          List with strings to be looked for in the comment field.
        
        Returns
        =======
        
        ---
        
        """
        # setup dates if needed
        if startDate == None:
            startDate = datetime.datetime(2000,1,1)
        if endDate == None:
            endDate = datetime.datetime.now()
        # convert keys into identifiers
        for k,s in enumerate(setups):
            if s in self.setups.keys():
                setups[k] = self.setups[s]
        for k,s in enumerate(projects):
            if s in self.projects.keys():
                projects[k] = self.projects[s]
        for k,s in enumerate(samples):
            if s in self.samples.keys():
                samples[k] = self.samples[s]
        for k,s in enumerate(types):
            if s in self.types.keys():
                types[k] = self.types[s]
        for k,s in enumerate(publications):
            if s in self.publications.keys():
                publications[k] = self.publications[s]
        
        sql = "SELECT * FROM measurements WHERE date BETWEEN '%s' AND '%s'" %(startDate,endDate)
        # add requirement for test
        if len(test) > 0:
            sql = sql + " AND ("
            for t in test[:-1]:
                sql = sql + "test = %s OR "%t
            sql = sql + "test = %s)"%test[-1]
        # add requirement for operator
        if len(operatorContains) > 0:
            sql = sql + " AND ("
            for op in operatorContains[:-1]:
                sql = sql + "operator LIKE '%"+op+"%' OR "
            sql = sql + "operator LIKE '%"+operatorContains[-1]+"%')"
        # add requirement for intention
        if len(intentionContains) > 0:
            sql = sql + " AND ("
            for i in intentionContains[:-1]:
                sql = sql + "intention LIKE '%"+i+"%' OR "
            sql = sql + "intention LIKE '%"+intentionContains[-1]+"%')"
        # add requirement for comment
        if len(commentContains) > 0:
            sql = sql + " AND ("
            for c in commentContains[:-1]:
                sql = sql + "comment LIKE '%"+c+"%' OR "
            sql = sql + "comment LIKE '%"+commentContains[-1]+"%')"
        # add requirement for types
        if len(types) > 0:
            sql = sql + " AND ("
            for t in types[:-1]:
                sql = sql + "type = %s OR "%t
            sql = sql + "type = %s)"%types[-1]
        # add requirement for setups
        if len(setups) > 0:
            sql = sql + " AND ("
            for s in setups[:-1]:
                sql = sql + "setup = %s OR "%s
            sql = sql + "setup = %s)"%setups[-1]
        # add requirement for samples
        if len(samples) > 0:
            sql = sql + " AND ("
            for s in samples[:-1]:
                sql = sql + "sample = %s OR "%s
            sql = sql + "sample = %s)"%samples[-1]
        # get measurements compatible with the above criterions
        [success,dbSamplesMeas] = self.executeSqlRequest(sql)

        # find measurements of given projects
        sql = "SELECT * FROM projectmeasurement"
        if len(projects) > 0:
            sql = sql + " WHERE "
            for p in projects[:-1]:
                sql = sql + "projectid = %s OR "%p
            sql = sql + "projectid = %s"%projects[-1]
        [success,dbSamplesProjMeas] = self.executeSqlRequest(sql)
        
        # find measurements of given publications
        sql = "SELECT * FROM publicationmeasurement"
        if len(publications) > 0:
            sql = sql + " WHERE "
            for p in publications[:-1]:
                sql = sql + "publicationid = %s OR "%p
            sql = sql + "publicationid = %s"%publications[-1]
        [success,dbSamplesPubMeas] = self.executeSqlRequest(sql)
        
        # get header 
        sql = "SELECT column_name FROM information_schema.columns WHERE table_name='measurements'"
        [success,dbHeader] = self.executeSqlRequest(sql)
        # reduces measurement list to valid measurements
        inds = []
        try:
            for k,mid in enumerate(dbSamplesMeas[:,0]):
                if len(publications)>0:
                     if mid in dbSamplesProjMeas[:,0] and mid in dbSamplesPubMeas[:,0]:
                            inds.append(k)
                else:
                    if mid in dbSamplesProjMeas[:,0]:
                        inds.append(k)
            # return reduced list
            return np.insert(dbSamplesMeas[inds,:],0,dbHeader.T,axis=0)
        except:
            # no measurement found
            return dbHeader.T
    
    def displayInfos(self):
        """
        Displays the required database entries and the available options to choose from.
        
        Parameters
        ==========
        
        ---
        
        Returns
        =======
        
        ---
        
        """
        print( "Required database keys:")
        print( "   %s"%self.reqDatabaseKeys)
        print( "Available setups:")
        print( "   %s"%self.properties['setups'].keys())
        print( "Available types:")
        print( "   %s"%self.properties['types'].keys())
        print( "Available samples:")
        print( "   %s"%self.properties['samples'].keys())
        print( "Available projects:")
        print( "   %s"%self.properties['projects'].keys())
    
    def createMeasurementEntry(self,mid,timestamp,path,databaseEntries):
        """
        Create the database entries of the current run.
        
        Parameters
        ==========
        
        databaseEntries: dict
          Dictionary specifying the database entries. Required keys are defined in self.db.reqDatabaseKeys.
        
        
        Returns
        =======
        
        boolean:
          True if successfully created the entry. False otherwise.
        
        """
        # define answer bool
        success = True
        # create sql request to enter in table measurements
        sql = "INSERT INTO measurements(mid, date, operator, folder, setup, type, intention, comment, sample, test)\
                 VALUES ('%s','%s','%s','%s',%i,%i,'%s','%s',%i,%s)"\
                 %(mid, 
                 str(timestamp).split(".")[0],
                 databaseEntries['operator'], 
                 path, 
                 self.properties['setups'][databaseEntries['setup']], 
                 self.properties['types'][databaseEntries['type']], 
                 databaseEntries['intention'], 
                 databaseEntries['comment'], 
                 self.properties['samples'][databaseEntries['sample']], 
                 databaseEntries['test'])
        [success, temp] = self.executeSqlRequest(sql)
        if not success:
            print("Could not generate database entry in table 'measurmenets'.")
        
        if success:
            # create sql request to enter in table projectmeasurements
            sql = "INSERT INTO projectmeasurement(mid, projectid) VALUES ('%s',%i)"\
                     %(mid, 
                     self.properties['projects'][databaseEntries['project']])
            [success, temp] = self.executeSqlRequest(sql)
            if not success:
                  print("Could not generate database entry in table 'projectmeasurements'.")
        return success
        
    def isComplete(self,databaseEntries):
        """
        Checks whether all the mandatory database entries are existent.
        
        Parameters
        ==========
        
        databaseEntries: dict
          Dictionary specifying the database entries.
        
        
        Returns
        =======
        
        Boolean.
        
        """
        complete = True
        for reqKey in self.reqDatabaseKeys:
            comp = False
            for key in databaseEntries.keys():
                if reqKey == key:
                    comp = True
                    break
            complete = complete and comp
            if not comp:
                print("Data structure not complete: ")
                print("  Missing database key %s"%reqKey)
                break
            else:
                if comp == 'setup':
                    if databaseEntries[comp] not in self.properties['setups'].keys():
                        print("Invalid database entry for key 'setup'.")
                        complete = False
                if comp == 'project':
                    if databaseEntries[comp] not in self.properties['projects'].keys():
                        print("Invalid database entry for key 'project'.")
                        complete = False
                if comp == 'sample':
                    if databaseEntries[comp] not in self.properties['samples'].keys():
                        print("Invalid database entry for key 'sample'.")
                        complete = False
                if comp == 'type':
                    if databaseEntries[comp] not in self.properties['types'].keys():
                        print("Invalid database entry for key 'type'.")
                        complete = False
        return complete
