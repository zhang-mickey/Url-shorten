## The assignment3 of web service and cloud-based system


This project is a simple URL shortener service built using FastAPI. 
It allows users to shorten URLs, retrieve original URLs, update stored URLs, and delete URLs. The service also includes a comprehensive test suite using unittest.



### Structure of the project
```
.
├── assignment3_2
│   ├── k8s
│   │   ├── auth-service
│   │   │   ├── charts
│   │   │   ├── templates
│   │   │   │   ├── tests
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   ├── serviceaccount.yaml
│   │   │   │   ├── Chart.yaml
│   │   │   └── values.yaml
│   │   ├── db-services
│   │   │   ├── charts
│   │   │   ├── templates
│   │   │   │   ├── tests
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   ├── serviceaccount.yaml
│   │   │   │   ├── Chart.yaml
│   │   │   └── values.yaml
│   │   ├── url-shorten-services
│   │   │   ├── charts
│   │   │   ├── templates
│   │   │   │   ├── tests
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   ├── serviceaccount.yaml
│   │   │   │   ├── Chart.yaml
│   │   │   └── values.yaml
├── auth_service
│   ├── Dockerfile
│   ├── auth_db.py
│   ├── requirements.txt
│   └── run_auth.py
├── db_services
│   ├── id_generator.cpython-312.pyc
│   ├── mode.cpython-312.pyc
│   ├── validate_url.cpython-312.pyc
│   └── Dockerfile
├── url_shorten_service
│   ├── Services
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run_url.py
│   └── url_db.py
├── README.md
├── docker-compose.yml
├── nginx.conf
└── requirements.txt

```


## How to run

### 3.1 for docker compose
```
cd assignment3
docker-compose build --no-cache 
docker-compose up

```


### 3.2 for k8s
Database (db-services) → Use ClusterIP
(auth-service, url-shorten-service) → Use ClusterIP
Expose Public Services via Ingress

#### deploy cluster
login and setup environment of VMs
```
ssh student038@145.100.130.38

aingiemie2Sie8ku

sudo apt-get update 

sudo apt-get install ca-certificates curl gnupg lsb-release

sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get -y install docker-ce docker-ce-cli containerd.io

sudo systemctl enable docker

sudo usermod -aG docker "$USER"

exit

ssh student038@145.100.130.38

aingiemie2Sie8ku

groups

sudo apt-get -y install apt-transport-https net-tools

sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update && sudo apt-get -y install kubelet kubectl kubeadm

sudo apt-mark hold kubelet kubectl kubeadm

```
setup control node
```
sudo systemctl restart containerd

sudo kubeadm reset -f

#Run the following command to verify that kubeadm can communicate with the container runtime:
sudo crictl info

sudo rm /etc/containerd/config.toml
sudo systemctl restart containerd

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd

sudo kubeadm reset -f
sudo systemctl restart containerd

echo "127.0.0.1 wscbs-038" | sudo tee -a /etc/hosts

IP=$(ip -4 -o a | grep -i "ens3" | awk '{print $4}' | cut -d '/' -f 1)

if [[ -z "$IP" ]]; then echo "Error: Could not find IP for ens3"; exit 1; fi

sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --control-plane-endpoint=$IP --apiserver-cert-extra-sans=$IP

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

#Verify it works
kubectl get nodes

sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
sudo systemctl status kubelet

#install Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml


[//]: # (sudo echo KUBELET_KUBEADM_ARGS="--network-plugin=cni --pod-infra-container-image=k8s.gcr.io/pause:3.2 --node-ip=$&#40;ip -4 -o a | grep -i "ens3" | cut -d ' ' -f 2,7 | cut -d '/' -f 1 | awk '{print $2}'&#41;" | sudo tee /var/lib/kubelet/kubeadm-flags.env)
sudo echo 'KUBELET_KUBEADM_ARGS="--container-runtime-endpoint=unix:///run/containerd/containerd.sock"' | sudo tee /var/lib/kubelet/kubeadm-flags.env

sudo kubeadm init phase kubelet-start
sudo systemctl restart kubelet
sudo systemctl status kubelet

sudo kubeadm reset

[//]: # (sudo journalctl -u kubelet --no-pager | tail -50)
# verify
kubectl get nodes -o wide
```

setup worker nodes
```
ssh student040@145.100.130.40

saiwie5ein2Shiob

#Run the following command to verify that kubeadm can communicate with the container runtime:
sudo crictl info

sudo rm /etc/containerd/config.toml

sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd

sudo kubeadm reset -f
sudo systemctl restart containerd

echo "127.0.0.1 wscbs-040" | sudo tee -a /etc/hosts

#On each worker node, run the kubeadm join command
sudo kubeadm join 145.100.130.38:6443 --token h3usob.iweeksm0xiffjzz2 \
	--discovery-token-ca-cert-hash sha256:c4602e71b60c9d8456ab23e56b450fc3b594d6c39c0880a1a0d1d0215fe97715 

```




#### deploy service
We have four service url_shorten_service,user_authentication_service,nginx,dabase

Helm Installation
```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```
##### Use Existing Helm Charts for Nginx ingress controller
```

[//]: # (Add the Nginx Ingress Controller Repository)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm search repo ingress-nginx

helm pull ingress-nginx/ingress-nginx
 
tar -zxvf ingress-nginx-4.12.0.tgz

[//]: # (Install Nginx Ingress Controllerkubectl get service)

helm install nginx-ingress ingress-nginx/ingress-nginx

kubectl patch svc ingress-nginx-controller -n default -p '{"spec": {"type": "NodePort"}}'

```
set up ingress
```

kubectl apply -f ingress.yaml
```

##### create deployment for for postresql db-service
```

[//]: # (helm repo add bitnami https://charts.bitnami.com/bitnami)
[//]: # (helm repo update)
[//]: # (helm install db-services bitnami/postgresql --set postgresqlPassword=123456 --set postgresqlDatabase=WSCBS_assignment --namespace default)

docker tag postgres:15 yuanzzy/webservice:db-services 

docker buildx build --platform linux/amd64 -t yuanzzy/webservice:db-services --push ./db_services

helm create db-services

[//]: # (Also disabled the liveliness and readiness probes for the deployment (kuberentes))


helm install db-services ./ --values values.yaml




```


##### create deployment for auth_service

We build the Docker Image Locally and Push Docker Image for auth-service to a Docker Repository
```
docker login


[//]: # (docker tag assignment2-auth_service:latest yuanzzy/webservice:auth-service)
[//]: # (docker tag assignment2-url_shorten_service:latest yuanzzy/webservice:url-shorten-service)

docker buildx build --platform linux/amd64 -t yuanzzy/webservice:url-shorten-service --push ./url_shorten_service

docker buildx build --platform linux/amd64 -t yuanzzy/webservice:auth-service --push ./auth_service

[//]: # (docker push yuanzzy/webservice:auth-service)
[//]: # (docker push yuanzzy/webservice:url-shorten-service)

```

```
scp  student038@145.100.130.38:
```


helm config
```
helm create auth-service

[//]: # (Modify the values.yaml File)
[//]: # (image:
[//]: # (  repository: "yuanzzy/webservice"
[//]: # (  tag: "auth-service" 
[//]: # (  pullPolicy: IfNotPresent)

helm install auth-service ./ --values values.yaml

```
##### create deployment for url-shorten-service
```
helm create url-shorten-service

helm install url-shorten-service ./ --values values.yaml
```





test
we need to modify the url first 
```
python test_app.py
```

```
kubectl exec auth-service-655c4b88c-7qhcn -- curl -X POST http://localhost:5001/users -H "Content-Type: application/json" -d '{"username":"test", "password":"value1"}'

kubectl exec auth-service-655c4b88c-7qhcn -- apt-get update && kubectl exec auth-service-655c4b88c-7qhcn -- apt-get install -y curl

```













