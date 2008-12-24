# Voice commands for dreamweaver

Open File    = {Ctrl+o};
Recent Files = {Alt+f};
Save File    = {Ctrl+s};
Save As      = {Ctrl+S};
Close That   = {Ctrl+w};

Show (Code=c | Design=d{Enter} | Both=a) = {Alt+v} $1;
Focus (Code=c | Design=d{Enter}) = {Alt+v} $1 {Alt+v}a{Down}{Up};
(Show|Hide|Toggle) Panels = {F4};
Refresh = {F5};
Show Preview = {F12};

Insert Row = {Ctrl+m};
Kill Row   = {Ctrl+M};

Style Mono = {Alt+t}st;
Style Heading 1..6 = {Ctrl+$1};
Style Normal = {Ctrl+0};

(Promote='[' | Demote=']') That = {Ctrl+Alt+$1};
