helm upgrade cy .\ --install --namespace cy
helm upgrade cy .\ --install --namespace cy --dry-run

#scale
helm upgrade cy .\ --install --namespace cy --set replicas=2 --debug
helm upgrade cy .\ --install --namespace cy --set requests.cpu=0.2 --set replicas=45 --debug

#delete
helm delete cy --namespace cy

#get into the pod works in pwsh and bash
kubectl exec -ti  -n cy $(kubectl get pods --no-headers -o custom-columns=":metadata.name" -n cy) -- bash

#describe
kubectl describe pod -n cy $(kubectl get pods --no-headers -o custom-columns=":metadata.name" -n cy)