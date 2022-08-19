import natlink as n
n.natConnect()
dis=n.natDisconnect
def bye():
    n.natDisconnect()
    quit()
p=n.playString

n.playString("naïve brachialis")