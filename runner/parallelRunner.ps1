#fixed iterations
param (
  [string]$tool = 'selenium', # selenium|playwright|cypress
  [int]$maxThreads =4,
  [int]$iterations = 4,
  [int]$rampUp = 2
)

$sleep = $rampUp / $maxThreads

$parallelTestJob = 1..$iterations | ForEach-Object -ThrottleLimit $maxThreads -Parallel {  
  $startAt = ($_ - 1) * $using:sleep;
  $tool = $using:tool;
  $cmd = ''
  $commands = @{
    cypress = "npm run cy:moon:edge --prefix=../cypress/" ;
    playwright = "npm run moon:firefox --prefix=../playwright/";
    selenium = "python ../selenium/test.py";
  }
 
  Start-Sleep $startAt; #delay iteration
  if($tool -ne 'all'){ #specific tool
    $cmd = $commands[$tool]
  } else{ #round robin
    switch ($_ % $commands.count) {
      0 { $cmd = $commands.cypress }
      1 { $cmd = $commands.playwright }
      2 { $cmd = $commands.selenium }
    }
  }
  "Iteration $_ running $cmd after $startAt, at CPU % ",(Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue; 
  Invoke-Expression "$cmd"
} -AsJob

$parallelTestJob | Receive-Job -Wait
