import natlink
import natlinkmain
import time

def run_waitForSpeechLoop():
    '''run the loop which waits for commands recognition
    
    this is only needed when natlink is not running automatically at Dragon startup
    '''
    try:
        while 1:
            natlink.waitForSpeech(0)
            print 'waited for speech'
    finally:
        natlink.natDisconnect()

if __name__ == '__main__':
    natlinkmain.start_natlink()
    run_waitForSpeechLoop()