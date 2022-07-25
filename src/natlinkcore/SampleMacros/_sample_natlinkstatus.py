"""_sample_natlinkstatus.py

Try the natlinkstatus.py output, and change load_on_begin_utterance property 

"""
#pylint:disable=W0401, W0614, C0115, C0116, W0613, R0201, W0603, E1101, W0201
import natlink
from natlinkcore.natlinkutils import *
from natlinkcore.natlinkstatus import NatlinkStatus
status = NatlinkStatus()

# prefer sendkeys method from dtactions:
try:
    from dtactions.sendkeys import sendkeys as playString
except ImportError:
    print('Cannot import sendkeys from dtactions')
    playString = natlink.playString



class ThisGrammar(GrammarBase):

    def initialize(self):
        """have global status instance and local localstatus instance...
        """
        self.localstatus = NatlinkStatus()
        if status.get_language() == 'nld':
            self.gramSpec = """
                <mainRule> exported = sampel natlinkstatus;
                <ruleChange> exported = setlood on biegin utterance (Troe|Fals|nul|een|twee|drie);
            """
        else:
            self.gramSpec = """
                <mainRule> exported = sample natlinkstatus;
                <ruleChange> exported = set load on begin utterance (True|False|zero|one|two|three);
        """

        self.load(self.gramSpec)
        self.activateAll()

    def gotResults_mainRule(self,words,fullResults):
        print(f'Saw <mainRule> = {repr(words)}')
        globalStatusString = status.getNatlinkStatusString()
        localStatusString = self.localstatus.getNatlinkStatusString()
        if localStatusString != globalStatusString:
            print('globalStatusString and localStatusString NOT EQUAL:')
            print('==========global:')
            print(globalStatusString)
            print('==========local:')
            print(localStatusString)
        else:
            print(globalStatusString)
            
    def gotResults_ruleChange(self,words,fullResults):  
        print('Saw <ruleChange> = %s{enter}' % repr(words))
        
        # if words[-1] in ["True", "Troe"]:
        #     newValue = True
        # elif words[-1] in ["False", "Fals"]:
        #     newValue = False
        # elif words[-1] in ["nul", "zero"]:
        #     newValue = 0
        # elif words[-1] in ["een", "one"]:
        #     newValue = 1
        # elif words[-1] in ["twee", "two"]:
        #     newValue = 2
        # elif words[-1] in ["drie", "three"]:
        #     newValue = 3
        # else:
        #     print(f'_sample_natlinkstatus, invalid word in rule: "{words[-1]}"')
        #     return
        # self.localstatus.set_load_on_begin_utterance(newValue)
        # value = self.localstatus.get_load_on_begin_utterance()
        # print(f'property "load_on_begin_utterance" is now: {value} (input was: {newValue})')

thisGrammar = ThisGrammar()
thisGrammar.initialize()

def unload():
    global thisGrammar
    if thisGrammar:
        thisGrammar.unload()
    thisGrammar = None

