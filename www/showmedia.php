<html>
<head><title>media info start</title></head>
<body>
<?php
 if($_GET['action'] == 'start'){
  exec('/usr/bin/pgrep -c -f showmewhatsplaying',$pids);
  //  echo count($pids);
  echo($pids[0]);
  if($pids[0]<=1) {
    echo exec ('/usr/bin/pkill -f showmewhatsplaying');
    exec('/usr/bin/python /home/pi/pyautomation/showmewhatsplaying.py > ccmedia.log 2>&1 &');
  }
  else
    {
      echo running; // restart anyway to force TV switch on
    echo exec ('/usr/bin/pkill -f showmewhatsplaying');
    exec('/usr/bin/python /home/pi/pyautomation/showmewhatsplaying.py > ccmedia.log 2>&1 &');
    }
 }

   else {
    echo exec ('/usr/bin/pkill -f showmewhatsplaying');
    }
?>
</body>
</html>
