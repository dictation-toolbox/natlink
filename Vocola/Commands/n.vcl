# Voice commands for n2
 

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
 
<Directions> := Up | Right | Left | Down | Enter | Delete |Backspace;
<Count> := 1..10;
<Modifiers> := (
				Alt | 
				Control = Ctrl| 
				Shift
				);
 
runs the command = " =  ;" {Left_2};
is equivalent to =  " =  |" {Left_2} ;
 
new keystroke [insert] = {end}{Left_2} {}{Left};
 
dollar <Count> = "$"$1 ;
direction <Directions> = $1 ;
direction <Directions> <Count> = $1_$2 ;
<Modifiers> <Letters> =  $1+$2;
