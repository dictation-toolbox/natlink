# Voice commands for Microsoft Visual Studio

include utilities.vch;

### Workspaces and Files

include folders.vch;
include   files.vch;

(Open=w | Close=k | Recent=r | Save=v) Workspace = {Alt+f} $1;
Workspace 1..10 = {Alt+f}r $1;

Open File          = {Ctrl+o};
Open File <folder> = {Ctrl+o} $1 {Enter};
Close (File|That) = {Alt+f}c;
Save File = {Ctrl+s};

Buffer <file> = {Ctrl+o} $1 {Enter};

Find in Files = {Alt+e}i;
Find in [Files] <folder> = {Alt+e}i{Tab_2} $1 {Shift+Tab_2};

[Toggle] Read Only = {Alt+f}a{Right}*{Enter}{Shift+Tab}{End}{Shift+F10}r
                     Wait(1000) {Alt+r}{Enter}{Esc};

### Editing and View

Full Screen = {Alt+v}u;
New (Search | Find) = {F3};
Find New = {Ctrl+f};
Find That = {Ctrl+F3};
Find (Down={F3} | Up={Shift+F3}) = $1;
Next Bookmark = {F2};

<digit> := 0..9;
Line Number = {Ctrl+g};
Line [Number] <digit> = {Ctrl+g} $1 {Enter};
Line [Number] <digit> <digit> = {Ctrl+g} $1 $2 {Enter};
Line [Number] <digit> <digit> <digit> = {Ctrl+g} $1 $2 $3 {Enter};
Line [Number] <digit> <digit> <digit> <digit> = {Ctrl+g}$1$2$3$4{Enter};

Output (Go="" | Start=Home | End) = {Alt+2}{Ctrl+$1};
Output Clear = moveNearEdge(sw,3,-4) ButtonClick(2,1) r;

### Builds

Rebuild = {F7};
Rebuild All = {Alt+b}r;
Project Settings = {Alt+F7};

### Debugging

(Set|Clear|Toggle) (Breakpoint={F9} | Bookmark={Ctrl+F2}) = $2;
[Edit] Breakpoints = {Alt+F9};
Remove [All] Breakpoints = {Alt+F9}{Alt+l}{Enter};
Exceptions = {Alt+d}e;
Reset Exceptions = {Alt+d}e{Alt+t} ControlPick(OK);

Continue = {F5};
Execute = {Ctrl+F5};
Restart = {Ctrl+Shift+F5};
Stop Debugging = {Shift+F5};
Break Now = {Alt+d}b;
Single Step = {F10};
