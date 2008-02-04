# Voice commands for NATSPEAK

Save File = {Ctrl+s};
Print (That|File) = {Ctrl+p}{Tab_4}{Ctrl+c}{Tab}{Ctrl+v}{Enter};

Find That = {Ctrl+f} ControlPick(Find Next) ControlPick(Cancel);
Find Again  = {F3};
Center in Window = {Down_30}{Up_30};

Reply Here = {Home}{Shift+End}{Del}{Enter_3}{Left_2};

Plain Text = {Ctrl+a}{Alt+o}fArial{Tab}Regular{Tab}10{Enter};

Vocabulary Editor:
  <n> := 0..99;
  <n> (Up | Down) = {Alt+w}{Tab_2}{$2_$1};
  (Written=w | Spoken=s) Form = {Alt+$1};