# Voice commands for ntvdm (Command Prompt)

include folders.vch;

Folder <folder> = 'cd "$1"{Enter}';

Copy That = {Enter};
Paste That = {Alt+Space}ep;

Go Up = "cd ..{Enter}";
Go Up 1..20 = "cd " Repeat($1, ..\) {Enter};
