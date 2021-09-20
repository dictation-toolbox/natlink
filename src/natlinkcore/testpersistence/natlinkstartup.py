## natlinkstartup faker

import natlinkstatus


def funcinnatlinkstartup():
    status = natlinkstatus.NatlinkStatus()
    name = status.getName()
    return name

def reportUserName():
    status = natlinkstatus.NatlinkStatus()
    print(f'userInfo from natlinkstartup: {status.getName()}')
    name = funcinnatlinkstartup()
    print(f'Name from userInfo from natlinkstartup: {name}')
