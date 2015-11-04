### 
### Module Keys
### 

import ExtendedSendDragonKeys
import SendInput



# Vocola procedure: Keys.SendInput
def send_input(specification):
    SendInput.send_input(
        ExtendedSendDragonKeys.senddragonkeys_to_events(specification))
