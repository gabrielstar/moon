#set cluster
az login
az aks list
az aks get-credentials --name committed --resource-group committed
az aks show --name committed --resource-group committed

#prep cluster
helm repo add aerokube https://charts.aerokube.com/
helm repo update
helm search repo aerokube --versions
kubectl create namespace moon

#install with defaults all specific configuration
helm upgrade --install -n moon moon aerokube/moon --version="1.1.12"

kubectl get all -nmoon
helm show values aerokube/moon

#change resource limits for autoscaling
helm upgrade --install -n moon moon aerokube/moon --version="1.1.12" --set moon.browser.resources.cpu.requests=0.8 --set moon.browser.resources.cpu.limits=2

#UI is at http://20.101.234.149:8080/#/
#server is at http://20.101.234.149:4444/wd/hub