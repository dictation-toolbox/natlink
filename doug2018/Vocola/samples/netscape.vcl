# Voice commands for Netscape 4  

### Reading email 
Netscape Folder: 
  New Message      = {Ctrl+m}; 
  Reply to Message = {Ctrl+r}; 
  Reply to All     = {Ctrl+Shift+r}; 
  Forward Message  = {Ctrl+l}; 

  Print Message = "{Ctrl+p}{Tab 6}1{Enter}"; 
  Search Messages = {Ctrl+Shift+F}; 

  Sort by (Date=e | Sender=r | Subject=s) = {Alt+v}o $1; 

  # Choose HTML editor or plain text editor 
  Use (HTML={Up} | Plain Text={Down}) =  
      "{Alt+e}e{Shift+Tab}{Down 8}{Tab}$1{Enter}"; 

  # Extract a file pathname from a mail message 
  Get File Name =  
      {Ctrl+l} Wait(500)           # Open a "forward" window 
     "{Enter 2}"                   # Move to message body 
      {Ctrl+f}:\{Enter}{Esc}       # Search for ":\" 
     "{Left 3}{Shift+End}{Ctrl+c}" # Copy entire pathname 
      {Alt+F4};                    # Close the window 

### Composing email messages 
Composition: 
  <EmailAddress> := ( David = dsmith@netscape.com 
                    | Emily = egreene@aol.com 
                    | Mike  = mike@orangerooster.com 
                    | Sue   = suenew@brown.net 
                    ); 
  Address <EmailAddress> = $1 {Enter}; 
  Cc <EmailAddress> = "{Shift+Tab} {Down 2}{Enter}$1{Enter}";  

  Send That = {Ctrl+Enter}; 

  I Meant Reply All = 
      {Ctrl+Home}{Ctrl+Shift+End}{Ctrl+c}  # Copy message 
      {Alt+F4}n                            # Close window 
      {Ctrl+Shift+r};                      # Reply to All 

### Editing HTML documents 
Netscape Composer: 
  Save (File|That) = {Ctrl+s}; 
  Save and Close   = {Ctrl+s}{Alt+F4}; 
  Show Preview     = {Ctrl+s} AppBringUp(iexplore) {F5}; 

  Fixed    Width [Font] = {Alt+o}{Right}{Down}{Enter};   
  Variable Width [Font] = {Alt+o}{Right}{Enter};   

  Style Normal         = {Alt+o}p{Enter}; 
  [Style] Heading 1..6 = {Alt+o}h $1; 

  Promote That = {Ctrl+-}; 
  Demote That  = SendSystemKeys("{Ctrl+=}");
