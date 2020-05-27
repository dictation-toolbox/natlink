# Voice commands for msedge
# https://support.microsoft.com/en-us/help/4531783/microsoft-edge-keyboard-shortcuts
mute tab = {Ctrl+m};
search web = {Ctrl+e};

#search web for <_anything> = "{Conrol+Shift+l}$1";   Cliboard required. 
select url = {Ctrl+l};
new window = {Ctrl+n};
show history = {Ctrl+h};
show downloads = {Ctrl+j};
reload = {Ctrl+r};
paste and go = {Ctrl+Shift+l};
#private window = {Ctrl+Shift+n};    #not working in Version 81.0.416.77 (Official build) (64-bit)

#searching within the page
find <_anything> = {Ctrl+f} $1;       
next match = {Ctrl+g};
previous match  = {Ctrl+Shift+g};


settings menu = {Alt+e};


#tabs
#speak tab x  to switch to the x'th tab.


close tab = {Ctrl+w};
<tabn> := 1..9;                    #possibly should allow 0 if Ctrl+0 ever works.
tab <tabn> = {Ctrl+$1}; 
(first=1) tab = {Ctrl+$1};         #documentation shows 0 should work but it doesn't.  use 1.   
(last=9) tab = {Ctrl+$1};
next tab = {Ctrl+Tab};
previous tab = {Ctrl+Shift+Tab};

#duckduckgo
#customize for yourfavorite bangs.  
#these are set up so you enter the search box first, then issue the bang command
(bang="!") (bing = b |image|video|(wyee tee=yt)| news|  b | bm | gee=g | (gee em)=gm | bmonotes | dig) = " $1$2 ";  #space before and after since you might put a bang at the end or beginning of a search.
bang="!" {" ! "};
