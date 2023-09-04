# Kubechat

Kubernetes bot powered by OpenAI GPTs. 

Use `ALT+Enter` to validate messages.

Use arrows to navigate through messages (history is saved at  ~/.kube-chat.history)

Use `/exit` to exit


## Prompts examples: 
> create/delete Deployment/StatefullSet/Configmap...

> add labels/probes/limits to all / StatefullSet and or Deployment(s)...

> add Service, Hpa, Ingress, etc...

> convert docker compose file into kubernetes resources:

## Run

```
pip install -r requirements.txt
export OPENAI_API_KEY=xxx-your-api-key

python3 kube_chat.py
```
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/jseguillon/kubechat-poc)
