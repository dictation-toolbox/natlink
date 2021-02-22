## natlinkstatus faker

class NatlinkStatus:
    def __init__(self):
        try:
            self.__class__.UserArgsDict
        except AttributeError:
            self.__class__.UserArgsDict = {}
            
    def setUserInfo(self, args):
        self.__class__.UserArgsDict['name'] = args[0]
        self.__class__.UserArgsDict['other'] = args[1]
    
    def getName(self):
        return self.__class__.UserArgsDict['name']
    
    def reportUserInfo(self):
        print(f'UserInfo: {self.__class__.UserArgsDict}')
    