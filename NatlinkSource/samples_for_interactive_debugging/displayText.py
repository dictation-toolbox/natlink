import natlink as n

n.natConnect()
dis=n.natDisconnect
def bye():
    n.natDisconnect()
    quit()

d=n.displayText
  
d("naïve brachialis",True,True)