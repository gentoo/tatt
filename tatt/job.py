"""Abstraction of a tatt job"""

class job(object):
    """A tatt job can have a
    - bugnumber
    - name
    - type (either 'stable', 'keyword')
    - list of packages
    """
    
    def __init__(self,
                 name="",
                 bugnumber=0,
                 type="stable",
                 packageList=None):
        self.name=name
        self.bugnumber=bugnumber
        self.type=type
        self.packageList=packageList

