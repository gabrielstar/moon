
## Load testing with a browser

When can you be tempted to do that ? When ...

- you have no other options (e.g. one cannot correlate the traffic at the protocol level)
- you want so make sure you do it "exactly" as end-user and cost is acceptable
- you want to simulate user traffic in the best way possible
- your tests are relatively small ane worth the expense

Bear in mind that generating load this way is a way more expensive thing than traditional, protocol-based approaches.

***

## Browser Load Testing with Selenium and Selenium Grid

Let us first see at how Selenium can be used to do that. It is a very popular technology and most tester should know it. 

Test is run from your test script, session is requested from grid hub and directed to one of the nodes. Nodes can start number of instances of different types: Chrome, Edge, ....

![grid](img/grid.drawio.png)

In our sample repo we can execute code from [selenium](selenium) and [grid](grid) folders

```powershell
    #run selenium with local driver - driver must match browser version
    cd selenium/
    python test.py

    #run against selenium grid
    cd grid/
    ./start-grid.ps1
    ./start-nodes.ps1 #navigate to http://localhost:4444/grid/console and read IP
    python test.py
```

If we want to use more than 1 browser at a time as load testing tool we need to run tests in parallel, which can be achieved:

- with code-specific mechanisms e.g. pytest-parallel, pytest-xdist, ... 
- with external controller e.g. a script, and since this is rare I want to show you how you can do it with [powershell](runner):

```powershell
    cd ./runner
    ./parallelRunner.ps1 #will run 4 parallel sessions

```
This way we can mix any kind of solution (playwright, cypress, selenium) in one. Of course you will not do it often ... but it is possible.

Great success, we can generate load from parallel browsers but ....

> what I really want is to run my test with 20 browsers:
> -  and I want that my browsers get created without me caring for it
> -  and so that infrastructure scales automatically.
> -  I want the same for 50 browsers, 70 , etc...


The solution we have allows us to run as many browsers as we can on our infrastructure but still within the limits of our nodes (their capacity =  nodes x slots/sessions). What we need for load tests is auto-scaling of both browsers instances and infrastructure. Let us see how we can achieve that with [Moon](https://aerokube.com/moon/) and [Kubernetes](https://kubernetes.io/pl/docs/concepts/overview/what-is-kubernetes/).

***

## Moon architecture

Moon is a commercial 'Browsers Grid' that runs on Kubernetes natively. It supports selenium, playwright and cypress as clients. For our case we can install Moon on Kubernetes and define scaling rules for:

- browser instances 
- hardware it runs on (kubernetes nodes)

![grid](img/moon.drawio.png)

Installation on AKS (Azure Kubernetes)

```powershell

    #prepare cluster
    az login
    az aks list --query "[*][name]"
    az aks get-credentials --name committed --resource-group committed 
    az aks show --name committed --resource-group committed

    #install moon
    helm repo add aerokube https://charts.aerokube.com/ 
    helm repo update 
    helm search repo aerokube --versions 
    kubectl create namespace moon
    helm upgrade --install -n moon moon aerokube/moon --version="1.1.12"

    #get EXTERNAL_IP from here
    kubectl get all -nmoon helm show values aerokube/moon

```

Moon will expose port 4444 for tests and 8080 for UI.

![moon](img/moon.png)


You can visit Moon UI at http://EXTERNAL_IP:8080

Let us try how it works with:
- selenium (modify URL in test)
```powershell
    cd selenium/
    python test.py
```
- playwright (modify URL in test)
```powershell
    cd ./playwright
    npm run moon:firefox
```
- cypress
```powershell
    cd ./cypress
    npm run cy:moon:edge
```

Now we can use again our runner once again to start 4 parallel sessions of cypress, selenium, playwright, ...

```powershell
    cd ./runner
    ./parallelRunner.ps1 #will run 4 parallel sessions
```

The only thing that is left is to turn on the AKS auto-scaling and configure limits on moon to tell kubernetes to create more nodes for our browser instances when needed.

***
## Kubernetes (auto-)scaling

![requests](https://blog.kubecost.com/assets/images/k8s-recs-ands-limits.png)
| https://blog.kubecost.com/blog/requests-and-limits/

[How can a k8 cluster scale](https://docs.microsoft.com/en-us/azure/aks/cluster-autoscaler) ?

![scaling](https://docs.microsoft.com/en-us/azure/aks/media/autoscaler/cluster-autoscaler.png)

| https://docs.microsoft.com/en-us/azure/aks/media/autoscaler/cluster-autoscaler.png

> The cluster autoscaler watches for pods that can't be scheduled on nodes because of resource constraints. The cluster then automatically increases the number of nodes.


To use auto-scaling we need to define resource requirements first for our browser instances:

```powershell
    #enable auto-scaling 
    helm upgrade --install -n moon moon aerokube/moon --version="1.1.12" --set moon.browser.resources.cpu.requests=1.5 --set moon.browser.resources.cpu.limits=3
```
As a second step we need to ensure our AKS has auto-scaler on (we do it in azure portal).

Our kubernetes has total of 3 CPUs x 2 cores = 6 cores. By running 4 tests (starting 4 browser instances) in parallel we want k8 to reserve 4 x 1.5 = 6 cores for the run. This should actually trigger auto scale-up because kubernetes uses some cpu for itself so in real life we do not have all 6 cores for ourselves.

Let us run our tests and wait for infrastructure to auto-scale too.
```powershell
    while($True) { kubectl get no; Start-Sleep 10 }
```
 It can take a couple of minutes but we should see node count going from 3 to 5 after some time.


*** 

## Alternative - using cypress (or anything else really) directly with Kubernetes.

If we have no need for Moon we can use any e2e testing framework, package it into a Docker container and deploy on Kubernetes with [Helm chart](https://helm.sh/) to take advantage of nodes auto-scaling.

![deployment](img/helm.png)


Let us dive into a sample kubernetes deployment in [kubernetes](../kubernetes) folder.

These will be useful commands:

```powershell
cd ./kubernetes/cypress/helm

#install
helm upgrade cy .\ --install --namespace cy --dry-run
helm upgrade cy .\ --install --namespace cy

#define browser instance requirements
helm upgrade cy .\ --install --namespace cy --set requests.cpu=0.2 --set replicas=45 --debug

#check number of instances - can take a while for all to pop up
kubectl get all -n cy

#delete
helm delete cy --namespace cy
```

When workload is installed, we can go and see how our application responds :)
It is possible that we will request a deployment that the cluster auto-sclaer cannot fullfill. In this case we need to modify auto-scaler policy.

***

## Doing all of that with CI - Azure DevOps

We should always aim at automating things. One way to do it is to create a pipeline for what we do.  Sample pipelines can be found in [azure](./azure) folder

![pipelines](img/pipeline.png)

We can run pipeline multiple times and observe our application monitoring.

***

Do not forget to clean up your cluster.

```powershell
    kubectl delete namespace moon
    kubectl delete namespace cy
```

