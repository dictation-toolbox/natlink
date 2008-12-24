# Voice commands for Mozilla

<EmailAddress> := ( Vocola      = vocola@attbi.com
                  | Voice Coder = VoiceCoder@yahoogroups.com
                  | Voice Group = VoiceGroup@yahoogroups.com
                  );

Java Console = {Alt+t}wj SendSystemKeys({Alt+Tab});

Compose:
  Address <EmailAddress> = $1 {Enter};
  See See <EmailAddress> = {Shift+Tab}{Down}{Home}{Down}{Enter}{Tab}$1{Enter};
  (To=1 | See See=2 | BCC=3) That
       = {Shift+Tab}{Down}{Home}{Down_$1}{Up}{Enter}{Tab};
  Kill Address = {Ctrl+Left_20}{Ctrl+Shift+Right_20}{Del_2};
  Send That = {Ctrl+Enter};
  I Meant Reply All = {Ctrl+Home}{Ctrl+Shift+End}{Ctrl+c}
                      {Alt+F4} Wait(100) "{Tab} " Wait(100) {Ctrl+Shift+r};
  Reply Here = {Home}{Shift+End}{Del}{Enter_2}{Left};
  Kill Message = {Alt+F4} Wait(100) "{Tab} ";

Mozilla:
  Get Messages     = {Ctrl+t};
  New Message      = {Ctrl+m};
  Reply to Message = {Ctrl+r};
  Reply to All     = {Ctrl+Shift+r};
  Forward Message  = {Ctrl+l};
  Forward As New   = {Ctrl+e};

  Print Message = "{Ctrl+p}{Tab 6}1{Enter}";

  Next Unread = {End}n;
  Kill and Read = {Del} Wait(100) {End}n;
  Kill (1|Line) = {Del};
  Kill 1..10 [Lines] = Repeat($1, {Del} Wait(100));

  (Flag|Unflag) That = {Alt+m}kf;
  First Flagged = {Alt+g}f;
  (Next  Flagged | Flag Down) = {Alt+g}nf;
  (Last  Flagged | Flag Up) = {Alt+g}pf;
  Mark All Read = {Ctrl+Shift+c};  

  include utilities.vch;
  rootFolder() := touchNearEdge(sw,1,-3) {Home};
  summary()    := touchNearEdge(sw,1,-3) {Tab_3};

  Folder (Inbox=1 | Sent=5) = rootFolder() {Down_$1}{Tab_3};
  Final Message = summary() {End};
  First Unread  = summary() {End}mn;
  Summary       = summary();
  Summary 1..20 (Up|Down) = summary() {$2_$1};

  Sort by (Date=e | Sender=n | Recipient=n | Subject=s | Thread=t | Flag=f)
      = {Alt+v}t $1;
  Search Messages = {Ctrl+Shift+F};
  Filter Messages = {Alt+s};
  Clear Filter = {Alt+c};

  (Open=o Wait(1000) {Enter} | Save=a) Attachment = {Alt+f}a{Right} $1;
  (Open=o Wait(1000) {Enter} | Save=a) Attachment 1..5 = {Alt+f}a $2 $1;
  (Save|Detach) All [Attachments] = {Alt+f}as;

  Switch Format = {Alt+e}m Wait(1000) "{Shift+Tab_4} {Enter}";

  Explore File = {Ctrl+l} Wait(1000) {Enter_2}{Alt+e}f Wait(1000) :\{Enter}
                 Wait(1000) {Left_2}{Shift+End}{Ctrl+c}{Alt+F4} Wait(1000)
                 HeardWord(switch, to, Windows, Explorer) Wait(1000)
                 "{Alt+d}{Ctrl+v}{Enter}{Tab 2}";

  Copy All = {Ctrl+a}{Ctrl+c};

  ### Browser

  include URLs.vch;

Composer:
  View (Normal=n | HTML=h) = {Alt+v} $1;
  Fixed Width    = {Alt+o}{Right}{Down}{Enter};  
  Variable Width = {Alt+o}{Right}{Enter};  
  Style Normal = {Alt+o}p{Enter};
  [Style] Heading 1..6 = {Alt+o}p $1;
  Save (File|That) = {Ctrl+s};
  Save and Close = {Ctrl+s}{Alt+F4};
  (Promote="[" | Demote="]") That = {Ctrl+$1};
