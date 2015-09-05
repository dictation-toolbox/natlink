instead of testnatlink now testing can be done with unittest:

- unittestNatlink.py
- unittestPrePost.py

=======================
Notes when testing with NatSpeak 10 (on Vista):

-after testing an extra natspeak instance remains active, even after closing NatSpeak (the DragonBar). This is also known to happen with voicecode. So you should check in the task manager whether all natspeak instances (processes) have been killed, for repeated testing (if strange things seem to happen)



Note

1. the icon file that is needed for one of the tests.

2. For version 9 all tests seemed to pass, also with the unimacro compatible version.
   For version 8 some differences make several tests fail, especially with testWordProns and testWordFuncs.
   Also testDictGram seems to fail, testPlaystring gives a strange (unresolved by me) error in version 8, maybe due to Dutch windows system.

3. The grammar files are not checked at each speech utterance, only when the microphone toggles.  This behaviour can be altered by the variable checkForGrammarChanges. In unimacro this option is set when you call (through the grammar _control) to change a grammar.

4. Testing with natconnectThreading set to 1 will fail some times.  So in other words this option is dangerous with several callback procedures.

5. Natlinkmain now always prints a message after starting, so the messages from python macros window always starts.  (Option that can be switched off)

6. Run most easily with IDLE, not with pythonwin. More instructions, also for one test at a time, in the top of the source file. 

Quintijn Hoogenboom,  May 1, 2007/February 2008
q.hoogenboom@antenna.nl, http://qh.antenna.nl/unimacro

Other things to test:
Various things of Unimacro in Unimacro/unimacro_test.
