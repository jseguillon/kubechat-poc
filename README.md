README.md

pip install -r requirements.txt

export OPENAI_API_KEY=xxx-your-api-key

python kube_chat.py


create a deployment php with min 2/CPUs max 5, min 1Go max 1.5. add a service and a disk of 5 Gi. then add an HPA to scale from 5 to 10 replicas when cpu reach 80%. then apply changes


convert docker compose file into kubernetes resources.
----
version: '3'
services:
  nginx:
   container_name: provectus-nginx
   image: nginx:1.13
   restart: always
   ports:
   - 80:80
   - 443:443
   volumes:
   - ./nginx/conf.d:/etc/nginx/conf.d
 
  mysql:
   container_name: provectus-mysql
   image: mysql/mysql-server:5.7
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

transform mysql deployement to statefulset 

add probes on both deployments and statefulsets
