# Voice commands for WINWORD

Save File = {Ctrl+s};
Save As = {Alt+f}A;
Recent Files = {Alt+f};
Recent File 1..4 = {Alt+f} $1;

(Outline=o | Normal=n | Print Layout=p | Web Layout=w) View = {Alt+v} $1;

# ---------------------------------------------------------------------------
# Manipulating Outlines

New Item         = {Ctrl+Down}{Left_2}{End}{Enter};
New Item Promote = {Ctrl+Down}{Left_2}{End}{Enter}{Alt+Shift+Left};
New Item Demote  = {Ctrl+Down}{Left_2}{End}{Enter}{Alt+Shift+Right};

Promote  That = {Alt+Shift+Left};
Demote   That = {Alt+Shift+Right};
Expand   That = {Alt+Shift+Plus};
Collapse That = {Alt+Shift+Minus};

Item (Up | Down)       = {Alt+Shift+ $1};
Item (Up | Down) 1..20 = {Alt+Shift+ $1 " " $2 };

# ---------------------------------------------------------------------------
# Styles

Style ( Normal
      | None = "Default Paragraph Font"
      ) = {Ctrl+S} $1 {Enter};

Heading 1..9 = SendSystemKeys({Ctrl+S}) "Heading " $1 {Enter}{Down};

Edit Style = {Alt+o} Wait(100) s{Alt+m}{Alt+o};

# ---------------------------------------------------------------------------
# Tables

Insert (Row Below=b|Row Above=a|Column Left=l|Column Right=r) = {Alt+a}i $1;

Merge Cells = {Alt+a}m;
Merge Row = {Alt+Home}{Shift+Alt+End}{Alt+a}m;

Align (Top=p | Center=c | Bottom=b) (Left=l | Center=c | Right=r) =
    {Alt+a}r{Alt+e}{Alt+ $1 }{Enter}{Alt+o}p{Alt+i}{Alt+g} $2 {Enter}{Enter};

# ---------------------------------------------------------------------------
# Miscellaneous

Find That = {Ctrl+c}{Ctrl+f}{Ctrl+v}{Enter}{Esc};
Replace Text = {Alt+e}e;

Keep with Next = {Alt+o}p{Alt+p}{Alt+x}{Enter};

(Subscript=b | Superscript=p) That = {Alt+o}f{Alt+ $1 }{Enter};
En Dash = {Ctrl+NumKey-};
Em Dash = {Ctrl+Alt+NumKey-};

Kill Here                  = {Shift+End}{Shift+Left}{Del};
Kill Back Here             = {Shift+Home}{Shift+Right}{Del};

Rosy Find = {Ctrl+f}{Enter}{Esc};
Rosy Do = {Home}{Shift+Down_2}{Del}{Ctrl+S}CodeHeading{Enter}{Down}{Del_13};

Accept or Reject Changes:
  Accept = {Alt+a};
  Reject = {Alt+r};
  Find = {Alt+f};

Find and Replace:
  Replace = {Alt+r};
  Replace All = {Alt+a};
  Find [Next] = {Alt+f};
