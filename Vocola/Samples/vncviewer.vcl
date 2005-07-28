# Voice commands for vncviewer

include utilities.vch;

Refresh = touchNearEdge(nw,1,1) r;
Close Session = touchNearEdge(ne,-1,1);

Local (Salute="" | Task Manager=t) =
    touchNearEdge(nw,1,1) {Down_11}{Enter} $1;

Local (Log Off="" | Restart={Down_2}) =
    touchNearEdge(sw,1,-1) {Up}{Enter} Wait(3000) {Home} $1 {Enter};

include remoteControl.vch;

### Start session on a specific machines
connect(machine, password, title) := $machine  {Enter} Wait(1000) 
                                     $password {Enter} Wait(3000)
                                     DllCall(SetTitle.dll, SetTitle, $title);
Connection details:
  Venus               = connect(Venus        ,rover  ,Venus);
  Developer Machine   = connect(dev-w2k      ,Spot   ,"Dev Machine");
  Mac Cube            = connect(192.168.1.79 ,cubist ,"Mac Cube");
