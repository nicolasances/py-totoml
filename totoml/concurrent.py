import os 

class ConcurrencyHelper: 
    """
    This class helps avoid race conditions when performing boot operations that should be 
    performed only once or that could introduce negative side effects when done in parrallel
    """
    def __init__(self, basefolder):
        """
        The init method. 

        Parameters
        ----------
        basefolder (str)
            The path of the base folder where all the model files are created

        """
        self.basefolder = basefolder
        self.lockfile = '{basefolder}/{name}'.format(basefolder=basefolder, name='lockfile')

    def lock(self): 
        """
        Creates a lock for critical operations
        If there is already a lock, this operation will fail and return False

        Returns
        -------
        locked (bool)
            Will return True if the lock is successfull, False otherwise
        """
        if os.path.exists(self.lockfile): return False

        f = open(self.lockfile, "w")
        f.close()

        return True
    
    def release(self): 
        """
        Releases a lock on critical operations
        """
        if os.path.exists(self.lockfile): 
            os.remove(self.lockfile)