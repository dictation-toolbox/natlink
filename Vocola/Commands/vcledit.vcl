# Voice commands for vcledit
 <Letters> := (
 Alpha = a|
 Bravo = b|
 Charlie = c|
 Delta = d|
 Echo = e|
 Foxtrot = f|
 Golf = g|
 Hotel  = h|
 India = i|
 Juliet = j|
 Kilo = k|
 Lima = l |
 Mike = m |
 November = n |
 Oscar = o |
 Papa = p |
 Quebec = q |
 Romeo = r |
 Sierra = s |
 Tango = t |
 Uniform = u |
 Victor = v|
 Whiskey = w |
 X-ray = x | 
 Yankee = y |
 Zulu = z 
 );




 <Directions> := (Up | Right | Left | Down | Enter | Delete = Del |Backspace);
 <Count> := 1..10;
 <Modifiers> := (
                                Alt | 
                                Control = Ctrl| 
                                Shift
                                );
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
