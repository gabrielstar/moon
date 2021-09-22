#fixed iterations
$tool = 'cypress'
$threads = 5;
$iterations = 6;
$rampUp = 20;
$sleep = $rampUp / $threads;


$job = 1..$iterations | ForEach-Object -ThrottleLimit $threads -Parallel {  
  $startAt = ($_ - 1) * $using:sleep;
  Start-Sleep $startAt;
  $cmd = ''
  switch ($using:tool) {
    'cypress' { $cmd = "npm run cy:moon --prefix=../cypress/" }
    'playwright' { $cmd = "playwright" }
    'selenium' { $cmd = "selenium" }
  }
  "Iteration $_ running $cmd after $startAt"; 
  Invoke-Expression "$cmd"
} -AsJob

$job | Receive-Job -Wait
