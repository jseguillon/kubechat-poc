# Kubechat

Kubernetes bot powered by OpenAI GPTs. 

Use `ALT+Enter` to validate messages.

Use arrows to navigate through messages (history is saved at  ~/.kube-chat.history)

Use `/exit` to exit


## Supported instrutions

```
create/delete Deployment/StatefullSet/Configmap...
add labels/probes/limits to all / StatefullSet and or Deployment(s)...
add Service, Hpa, Ingress, etc...
apply all/only Deployment nginx
```


## Install requirements
```
pip install -r requirements.txt
```

## Run

```
export OPENAI_API_KEY=xxx-your-api-key

python3 kube_chat.py
```


## Sample conversation

### Common php

```
create a deployment php with min 2/CPUs max 5, min 1Go max 1.5. add a service and a disk of 5 Gi. 
then add an HPA to scale from 5 to 10 replicas when cpu reach 80%. then apply changes
```

# Docker compose convert

```
convert docker compose file into kubernetes resources:

----
version: '3'
services:
  nginx:
   container_name: sample-nginx
   image: nginx
   restart: always
   ports:
   - 80:80
   - 443:443
   volumes:
   - ./nginx/conf.d:/etc/nginx/conf.d
 
  mysql:
   container_name: sample-mysql
   image: mysql/mysql-server
   environment:
    MYSQL_DATABASE: root
    MYSQL_ROOT_PASSWORD: 143625
    MYSQL_ROOT_HOST: '%'
   ports:
   - "3306:3306"
   restart: always
  
  app:
    restart: always
    build: ./app
    working_dir: /app
    volumes:
      - ./app:/app
      - ~/.m2:/root/.m2
    expose:
      - "8080"
    command: mvn clean spring-boot:run
    depends_on:
      - nginx
      - mysql
```

Then 

```
transform mysql deployement to statefulset 
```
