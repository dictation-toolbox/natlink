import natlink as n

n.natConnect()
dis=n.natDisconnect
def bye():
    n.natDisconnect()
    quit()

e=n.execScript
  
e('SendKeys "naïve brachialis"')