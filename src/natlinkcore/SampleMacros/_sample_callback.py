"""_sample_callback.py

Try/show the callback functions of the natlinkmain instance.

"""
#pylint:disable=W0401, W0614, C0115, C0116, W0613, R0201, W0603, E1101, W0201
from natlinkcore.natlinkutils import *
from natlinkcore import loader

natlinkmain = loader.NatlinkMain()

class ThisGrammar(GrammarBase):

    def initialize(self):
        """have global status instance and local localstatus instance...
        """
   
    def pre_load_callback(self):
        print('------- pre_load_callback')
    def post_load_callback(self):
        print('------- post_load_callback')
    def on_mic_on_callback(self):
        print('------- on_mic_on_callback')
    def on_begin_utterance_callback(self):
        print('------- on_begin_utterance_callback')
        
thisGrammar = ThisGrammar()
thisGrammar.initialize()
natlinkmain.set_on_begin_utterance_callback(thisGrammar.on_begin_utterance_callback)
natlinkmain.set_on_mic_on_callback(thisGrammar.on_mic_on_callback)
natlinkmain.set_pre_load_callback(thisGrammar.pre_load_callback)
natlinkmain.set_post_load_callback(thisGrammar.post_load_callback)

def unload():
    global thisGrammar
    if thisGrammar:
        natlinkmain.delete_on_begin_utterance_callback(thisGrammar.on_begin_utterance_callback)
        natlinkmain.delete_on_mic_on_callback(thisGrammar.on_mic_on_callback)
        natlinkmain.delete_pre_load_callback(thisGrammar.pre_load_callback)
        natlinkmain.delete_post_load_callback(thisGrammar.post_load_callback)
        # extraneous deletes do not harm:
        natlinkmain.delete_pre_load_callback(thisGrammar.pre_load_callback)
        thisGrammar.unload()
    thisGrammar = None



