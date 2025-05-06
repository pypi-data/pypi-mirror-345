"""
    !!! Warning: You need to add the module 'itsa' to your Python path to use
    these functions

    ----
    Developed at: ISTerre
    By: Lou MARILL
"""


#############################
def find_posformat(pos_file):
    """
    Find pos format of |file_pos|

    Parameters
    ----------
    pos_file : str
        Name of the file (and path).

    Raises
    ------
    TypeError
        If |pos_file| does not have the right type.
    FileNotFoundError
        If |pos_file| does not exist.

    Returns
    -------
    str
        Pos format of |pos_file|:
            'PBO': PBO pos format,
            'GX': GipsyX pos format,
            'F3': F3 solution pos format,
            'NGL': Nevada Geodetic Laboratory solution pos format.

    """

    # Import
    from os.path import exists
    from linecache import getline

    # Check parameter
    if not isinstance(pos_file, str):
        raise TypeError('Name of the file must be str: |type(file_pos)=%s|.'
                        % type(pos_file))
    if not exists(pos_file):
        raise FileNotFoundError('%s file not found.' % pos_file)

    # Look first line of the file
    try:
        line = getline(pos_file, 1).split()[0]
        if line == 'PBO':
            return 'PBO'
        elif line == 'YYYY':
            return 'GX'
        else:
            return 'NGL'
    except:
        return 'F3'
