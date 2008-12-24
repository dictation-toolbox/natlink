# Voice commands for Internet Explorer

include URLs.vch;

Address = {Alt+d};
(Copy=c | Paste=v) (Address|URL) = {Alt+d}{Ctrl+$1};

Go (Back=Left | Forward=Right)      = {Alt+$1};
Go (Back=Left | Forward=Right) 1..9 = {Alt+$1_$2};
Go Home = {Alt+Home};
Refresh = {Alt+v}r;

New Window = {Ctrl+n};
Open Window = ButtonClick(2,1) {Down_2}{Enter};
View Source = {Alt+v}c;

Web Search = {Alt+g};
(Show|Hide|Kill) Favorites = {Ctrl+i};
Java Console = {Alt+v}j SendSystemKeys({Alt+Tab});
Proxy Server = {Alt+t}o{Shift+Tab}{Right_4}{Alt+l}{Tab+2};

Find Down = {Ctrl+f};

Small Text = {Alt+v}xs;
