We are well underway to make a new stable release for Dragon 12 and NatLink too. (September, 2 2013)


In the 4.1golf release the config program has been improved: the (Re) Register NatLink function now works better and also copies the correct pyd file from the PYD subdirectory. Also a workaround for the sendkeys bug in Dragon is tried: use the S Unimacro Shorthand Command in Vocola command files. In Unimacro each doKeystroke call is started with an extra {shift}.

In this 4.1foxtrot release some changes were made in the config program 
In the 4.1echo release the natlink.pyd file from 4.1charlie is restored, as there were problems with the 4.1delta version.
See the discussion on http://www.speechcomputing.com/node/7661

-This includes a new stable Vocola release which is complete implemented in python

-NatLink can be used with python 2.6 and python 2.7.

-Note that with Dragon 12, you should NOT use the speech model BestMatch V, which is used by default on most computers when create a new User Profile.

-Python 2.5 still can be used, but only for Dragon <= 11.

Consider to make a small donation to the 3 people who do most work for this development:
-Rudiger Wilke, working on the heart of the program, the NatLink core
-Mark Lillibridge, maintaining and improving Vocola 2
-Quintijn Hoogenboom, working at Unimacro and the installer stuff 