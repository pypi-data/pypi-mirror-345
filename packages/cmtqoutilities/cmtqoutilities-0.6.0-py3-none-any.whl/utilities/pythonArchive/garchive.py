from __future__ import division
import os, sys
import glob
from datetime import date
import numpy as np

class garchive(dict):
    """ Store data in the standard group format!
    
    Notes
    -----
    
    Data layout principles: 
    
        - There are the following mandatory meta fields:
            
            - 'operator'      : string with responsible persons first & last name
            
            - 'intention'   : string describing the intention when the data was 
                              taken/calculated
            
            - 'setup'       : string describing the setup
            
            - 'type'       : string describing the type
            
            - 'sample'     : string telling which sample
            
            - 'parameters'  : dict with all parameters needed to reproduce the 
                              data. The purpose of this field is to be used 
                              when creating a database. Moreover, having this
                              set allows for quickly checking the parameters
                              when an archive object is loaded.

        - There are two data fields, both of which are optional:
            
            - 'data'     : python dictionary containing data.
                           This field is intended for 'processed' data, or data
                           that represents measurements of raw_data in the case
                           where storing all of the raw_data would be too much.

            - 'raw_data' : python dictionary containing raw_data.
                           This field is intended for storing the raw, 
                           unprocessed data.
    
            Internally, the data and raw_data dictionaries are compressed 
            (separately) before beign written to a file. Compression on data 
            and raw_data is done by bz2 on a cPickle-string-dump. The whole 
            archive is then cPickled again when stored as a file on disk. 
        
        - Other fields
            
            The user may add any number of other fields to the garchive, none
            of which will be checked for consistency (unlike the above mandatory
            fields), nor will they be compressed (like the data and raw_data 
            fields).
    
    """
    def __init__(self, *args, **kw):
        """ Initialize object

        Initializes standard dictionary, but stores garchive specific properties
        such as date of creation.

        """
        super(garchive,self).__init__(self)
        self.date = date.today()

    def __setitem__(self, key, value):
        """ Set a (key,value) pair in the garxiv dictionary

        This function simply overrides the __setitem__ method of the python 
        dictionary, but includes a few checks on the keys and their respective
        values that are being set.

        """
        if key in ["operator", "intention", "setup","type","sample","parameters"] and value == "":
            raise Exception("Cheating not allowed, required fields cannot be empty")

        # data and raw_data fields should be dictionaries (or strings, but only if compressed as string)
        if (key == 'data' or key == 'raw_data') and not (isinstance(value, dict)):
            raise Exception("The 'data' field should be a dictionary.")

        # If we made it this far, all checks passed
        super(garchive,self).__setitem__(key, value)

    def __check_consistency(self):
        """ Check garchive for consistency

        Performs checks on keys (i.e. their presence mostly).

        """
        # Check if required fields are set
        required_keys = ["operator", "intention", "setup","type","sample","parameters"]
        for key in required_keys:
            if not self.__contains__(key):
                raise Exception("No '%s' field set."%key)

        if self.__contains__('raw_data') and not self.__contains__('raw_doc'):
            raise Exception("Documentation for raw_data not set!")

    def save(self, directory, filename="", filetag="file"):
        """ Save archive to file

        Notes
        -----
            Saves the archive to a file. This function checks for consistency of the
            archive before saving.

        Parameters
        ----------
            - directory     : string pointing to directory in which to save 
                              archive. Will be created if it doesn't exist.
            - filename      : filename for file to be saved as. If left 
                              empty, will be stored using a year_month_day
                              format with a counter
            - filetag       : Optional tag for default filename. Only used
                              if filename is left emtpy, to have some
                              control over filename.

        Returns
        -------
            - fullname      : string with filename, including directory.

        """
        # Save garchive to file, compressing data but not metadata
        self.__check_consistency()

        # Check if filetag is legal
        if filetag.find('_') != -1:
            raise Exception("The character _  is not allowed in filetag.")
        
        # Create directory if it doesn't exist yet
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        
        # Create a filename if none was specified
        if filename == "":
            basename  = "%s_" %(filetag)
            files     = np.sort(glob.glob(directory + "/" + basename +"*.npz"))
            latest    = np.max( [-1] + [int( (file.split("_")[-1]).split(".")[0] ) for file in files] )
            filename  = "%s%05d.npz"%(basename, latest + 1)

        # cPickle dump to file
        np.savez(directory + "/" + filename,[self])
        
        # Return filename
        return filename
    
    
    def load(self, directory, filename):
        """ Load archive from file

        Parameters
        ----------
            - filename          : full path and filename

        """
# <<<<<<< HEAD
#         loaded=np.load(directory + "/" + filename)
#
#         data=loaded[loaded.files[0]][0]
# =======
        loaded=np.load(directory + "/" + filename,allow_pickle=True)
        data=loaded[list(loaded.keys()) [0]][0]
# >>>>>>> e52b4daeab54296dff78eaeaa39f4f809103b337
        
        # Set current instance fields
        for key in data.keys():
            self.__setitem__(key, data[key])

        self.date = data.date
