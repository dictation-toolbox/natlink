# Voice commands for vcledit
<Letters> := (
Alpha = a | Bravo = b|
Charlie = c | Delta = d|
Echo = e | Foxtrot = f|
Golf = g| Hotel  = h| India = i|
Juliet = j| Kilo = k|
Lima = l | Mike = m |
November = n | Oscar = o |
Papa = p | Quebec = q |
Romeo = r | Sierra = s | Tango = t |
Uniform = u | Victor = v|
Whiskey = w | X-ray = x | 
Yankee = y | Zulu = z );
 
<Directions> := (Up | Right | Left | Down | Enter | Delete = Del |Backspace);
<Count> := 1..10;
<Modifiers> := ( Alt | Control = Ctrl | Shift );

runs the command = " =  ;" {Left_2};
is equivalent to =  " =  |" {Left_2} ;
new keystroke [insert] = {end}{Left_2} {}{Left};
new list [insert] = {Left}{Ctrl+Right} " <> " {Left_2};
refresh macros = {Ctrl+s}
                                SetMicrophone(0)
                                SetMicrophone(1) ;
 
dollar <Count> = "$"$1 ;
direction <Directions> = $1 ;
direction <Directions> <Count> = $1_$2 ;
direction <Directions> dollar <Count> = $1 "_" $$2 ;
<Modifiers> <Letters> =  $1+$2;
<Modifiers> <Letters> <Count> = $1+$2_$3;
<Modifiers> <Letters> dollar <Count> = $1+$2 "_" $$3;
<Modifiers> <Modifiers> <Letters> = $1+$2+$3;
<Modifiers> [direction] <Directions> = $1+$2;
<Modifiers> [direction] <Directions> <Count> = $1+$2_$3;
<Modifiers> [direction] <Directions> dollar <Count> = $1+$2 "_" $$3;
<Modifiers> <Modifiers> [direction] <Directions>  = $1+$2+$3;
<Modifiers> <Modifiers> [direction] <Directions> <Count> = $1+$2+$3_$4;
<Modifiers> <Modifiers> [direction] <Directions> dollar <Count> = $1+$2+$3 "_" $$4;

insert range 0..99 to 0..99  = $1".."$2 ;

insert Repeat = "Repeat()"{left} ;
insert Active Menu Pick =   "ActiveMenuPick()"{left};
insert Active Control Pick =  "ActiveControlPick()"{left} ;
insert App Bring Up = "AppBringUp(APPNAME,APPPATH)"{left} ;
insert App Swap With = "AppSwapWith(APPNAME)"{left} ;
insert Beep = "Beep()";
insert Left Button Click = "ButtonClick(1,1)";
insert Right Button Click = "ButtonClick(2,1)" ;
insert Left Button Double Click = "ButtonClick(1,2)" ;
insert Right Button Double Click = "ButtonClick(1,2)" ;
insert Clear Desktop = "ClearDesktop()";
insert Control Pick = "ControlPick(CONTROLNAME)"{left} ;
insert DDE Execute = "DdeExecute(APP, TOPIC, COMMANDSTRING)"{left} ;  
insert DDE Poke = "DdeExecute(APP, TOPIC, ITEM, VALUE)"{left} ;
insert DLL Call = "DllCall(LIB, FUNC, STRINGARG)"{left} ;
insert Drag To Point (Left = 1 | Right = 2 | Middle = 4 ) = "DragToPoint(" $1 ")";
insert eval = "Eval()"{Left} ;
insert eval template = "EvalTemplate()"{Left} ;
insert Go To Sleep = "GoToSleep()"{left} ;
insert Menu Cancel = "MenuCancel()" ;
insert MenuPick = "MenuPick()" {Left} ;
insert Mouse Grid = "MouseGrid()" ;
insert Message box confirm = "MsgBoxConfirm(MESSAGE, TYPE, TITLE)" {left} ;
insert Play Sound = "PlaySound( WAVEFILE )" {left};
insert Remember Point = "RememberPoint()" ;
insert Repeat = "Repeat()"{left} ;
insert Run Script File = "RunScriptFile(COMMAND_FILE)" ;
insert Send Keys = 'SendKeys("")' {Left_2};
insert Send System Keys = 'SendSystemKeys("{}")'{Left_2} ;
insert Set Microphone (On =1 | Off = 0 ) = 'SetMicrophone('$1')' ;
insert Set Natural Text = "SetNaturalText(1)" ;
insert ShellExecute = 'ShellExecute("COMMAND")' ;
insert Shift Key (Shift=1 | Control=2 | Alt=3) = "ShiftKey($1)" ;
insert TTS Play String = "TTSPlayString()" {left} ;
insert Wait 1..1000 = "Wait("$1")" ;
insert Wake Up = "WakeUp()" ;
insert WinHelp = "WinHelp()" {left} ;
insert Set Mouse Position 1..99 by 1..10 =  "SetMousePosition (1, $1 , $2 )" ;
#the following commands are useful for entering heard words.
#Start by saying "insert Heard Word Go" then say "next word back" this inserts
#the command "HeardWord("go","back");"
next word <_anything>= {right_2} ',"' $1 '"' {Left};
nsert Heard Word <_anything> = 'HeardWord("$1")' {Left_2} ;
new choice list = ":= ();"{Left_2} ;
or = "|" ;
control key <Modifiers> = $1;
