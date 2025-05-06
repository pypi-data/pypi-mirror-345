"""
    Developed at: ISTerre
    By: Lou MARILL
"""


###############
def copy(self):
    """
    Copy Jps

    Return
    ------
    jps : Jps
        New Jps from |self|.
        
    """

    # Check parameters
    self.check_jps()

    # Import
    from copy import deepcopy

    # Copy
    jps = deepcopy(self)

    # Return
    return jps
