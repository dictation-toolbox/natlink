## natlinkmain faker

import natlinkstatus
import natlinkstartup

def setUserArgs(args):
    """pass on to natlinkstatus
    """
    natlinkstatus.setUserInfo(args)
    
if __name__ == "__main__":
    status = natlinkstatus.NatlinkStatus()
    status.setUserInfo( ('qqqq', 'other info') )
    status.reportUserInfo()
    natlinkstartup.reportUserName()
    status.setUserInfo( ('doug', 'relevant info'))
    natlinkstartup.reportUserName()
    