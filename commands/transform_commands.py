# 3rd layer prompt: get transformation python code and run to get update
import logging
import time, random
import ast
from .base_commands import KubeCommand, OneShotCommand, KubeChatAnswer

class TransformCommand(OneShotCommand):
    command = '/transform'
    description = "Transform prompt"
    parameters = []
    command_name='transform'
    include_items = True
    stream = False
    sanitize_code_answer = True

    model="gpt-3.5-turbo"
    openai_params = {
        'temperature': 0,
        'max_tokens': 3000,
        'request_timeout': 60,
        'stream': stream
    }

    ## FIXME: go back to Oneshot prompt and reactivate target items on do_action for best perfs ! 
    generic_message = """You are a Kubernetes expert and unique goal is to modify a variable named 'current_items' which reflects extract of existing items from a cluster.
You analyze user need and output python script that changes current_items to reflect new desired cluster status.
You dont add comments nor explanations nor block codes, only pure python. You dont use Kubernetes API. You import no library.
You cant directly act on server but only via current_items manipulation.
Dont redefine already existing items unless necessary. Dont create for loops nor use if conditions. Never set 'status' key.

Now reply python script to change current_items:"""

    template_message = """You are a Kubernetes expert and unique goal is to append content to 'current_items' variable which reflects extract of existing items from a cluster.
You output python that modifies current_items to reflect new desired cluster status. You dont add comments nor explanations nor block codes, only pure python.
You cant directly act on server but only via current_items. You never set 'status' key.
"""

    dp_tpl = {'apiVersion': 'apps/v1', 'kind': 'Deployment', 'metadata': {'name': 'myname', 'namespace': 'myns' }, 'spec': {'selector': {'matchLabels': {'app': '' }}, 'replicas': 1, 'template': {'metadata': {'labels': {'app': ''}}, 'spec': {'containers': [{'name': '', 'image': '', 'ports': [ ], 'resources': {}, 'imagePullPolicy': 'Always'}]}}}}
    pvc_tpl = {'apiVersion': 'v1', 'kind': 'PersistentVolumeClaim', 'metadata': {'name': 'myname', 'namespace': 'myns'}, 'spec': {'accessModes': ['ReadWriteOnce'], 'volumeMode': 'Filesystem', 'resources': {'requests': {'storage': ''}}}}
    hpa_tpl = {'apiVersion': 'autoscaling/v2', 'kind': 'HorizontalPodAutoscaler', 'metadata': {'name': 'myname','namespace': 'myns'}, 'spec': {'scaleTargetRef': {'apiVersion': 'apps/v1', 'kind': '', 'name': ''}, 'minReplicas': 1, 'maxReplicas': 10, 'metrics': [{'type': 'Resource', 'resource': {'name': 'cpu', 'target': {'type': 'Utilization', 'averageUtilization': 50}}}]}}
    pdb_tpl= {'apiVersion': 'policy/v1', 'kind': 'PodDisruptionBudget', 'metadata': {'name': 'myname','namespace': 'myns'}, 'spec': {'minAvailable': 1, 'selector': {'matchLabels': {'app': ''}}}}
    svc_tpl= {'apiVersion': 'v1', 'kind': 'Service', 'metadata': {'name': 'myname','namespace': 'myns'}, 'spec': {'ports': [{'name': 'http', 'port': 80, 'targetPort': 80}], 'selector': {'app': 'nginx'}}}
    sts_tpl = {'apiVersion': 'apps/v1', 'kind': 'StatefulSet', 'metadata': {'name': 'myname','namespace': 'myns'}, 'spec': {'selector': {'matchLabels': {'app': ''}}, 'serviceName': '', 'replicas': 1, 'template': {'metadata': {'labels': {'app': ''}}, 'spec': { 'containers': [{'name': 'nginx', 'image': '', 'ports': [], 'volumeMounts': [{'name': '', 'mountPath': ''}]}]}}, 'volumeClaimTemplates': [{'metadata': {'name': ''}, 'spec': {'accessModes': ['ReadWriteOnce'], 'storageClassName': '', 'resources': {'requests': {'storage': ''}}}}]}}
    cronjob_tpl = {'apiVersion': 'batch/v1', 'kind': 'CronJob', 'metadata': {'name': 'myname','namespace': 'myns'}, 'spec': {'schedule': '', 'jobTemplate': {'spec': {'template': {'spec': {'containers': [], 'restartPolicy': 'OnFailure'}}}}}}
    ds_tpl =  {'apiVersion': 'apps/v1', 'kind': 'DaemonSet', 'metadata': {'name': 'myname', 'namespace': 'myns', 'labels': {'k8s-app': ''}}, 'spec': {'selector': {'matchLabels': {'name': ''}}, 'template': {'metadata': {'labels': {'name': ''}}, 'spec': {'tolerations': [{'key': 'node-role.kubernetes.io/control-plane', 'operator': 'Exists', 'effect': 'NoSchedule'}], 'containers': []}}}}
    cm_tpl = {'apiVersion': 'v1', 'kind': 'ConfigMap', 'metadata': {'name': 'myname','namespace': 'myns'}, 'data': {}}
    sec_tpl = {'apiVersion': 'v1', 'kind': 'Secret', 'metadata': {'name': 'myname','namespace': 'myns'}, 'data': {}}
    ing_tpl = {'apiVersion': 'networking.k8s.io/v1', 'kind': 'Ingress', 'metadata': {'name': 'myname', 'namespace': 'myns','annotations': {'nginx.ingress.kubernetes.io/rewrite-target': '/'}}, 'spec': {'ingressClassName': 'nginx', 'rules': [{'http': {'paths': [{'path': '/path', 'pathType': 'Prefix', 'backend': {'service': {'name': 'test', 'port': {'number': 80}}}}]}}]}}
    templates_map = [{'kind': 'Deployment', 'template': f"{dp_tpl}"},
        {'kind': 'PersistentVolumeClaim', 'template': f"{pvc_tpl}"},
        {'kind': 'PodDisruptionBudget', 'template': f"{pdb_tpl}"},
        {'kind': 'HorizontalPodAutoscaler', 'template': f"{hpa_tpl}"}, 
        {'kind': 'Service', 'template': f"{svc_tpl}"}, 
        {'kind': 'StatefulSet', 'template': f"{sts_tpl}"},
        {'kind': 'CronJob', 'template': f"{cronjob_tpl}"},
        {'kind': 'DaemonSet', 'template': f"{ds_tpl}"},
        {'kind': 'ConfigMap', 'template': f"{cm_tpl}"},
        {'kind': 'Secret', 'template': f"{sec_tpl}"},
        {'kind': 'Ingress', 'template': f"{ing_tpl}"},
        ]
    rules = [
            {'kind': 'Deployment', 'rule': "- for each Deployment you create: set ports plus cpu/memory limits and requests unless user explicitly tells opposite"},
            {'kind': 'PersistentVolumeClaim', 'rule': "- if user ask for adding disk or pvc to a deployment X, you must create the pvc then mount it in Deployment X"},
            {'kind': 'Service', 'rule': "- if modifying Deployement, ensure not to duplicate existing containerport"},
        ]

    def new_message(self, intent, text, items, to_create_items_list_param=[], to_change_items_list = [],**user_params):
        # TODO inject flatten items
        logging.debug(f'New message {self.command} - {self.model} with text: {text}, params: {user_params} and files: {items}')

        
        if to_create_items_list_param !=[]:
            self.print_slow(f"KubeChat: creating new items {to_create_items_list_param}.\n", 6000)
        if to_change_items_list !=[]:
            self.print_slow(f"KubeChat: updating {to_change_items_list}.\n", 6000)
        target_items = items.copy()

        new_items_hint=""
        if (len(to_create_items_list_param) >0 ):
            finish_prompt = "Now only answer pure python, no comment:"
            # Add templates
            self.system_message = self.template_message
            kinds = [item['kind'].upper() for item in (to_create_items_list_param)]
            # if 'DEPLOYMENT' in kinds and 'SERVICE' not in kinds:
            #     kinds+=['SERVICE']
            self.system_message += "\n\Examples you may use:"
            for tpl in self.templates_map: 
                if tpl['kind'].upper() in kinds:
                    self.system_message += "\n- " + tpl['kind'] + " Example " + ": " + tpl['template']  
            
            # Add Rules
            rules=""
            for rule in self.rules: 
                if rule['kind'].upper() in kinds:
                    rules += f"\n{rule['rule']}"
            if not rules == "":
                self.system_message += "\n\n Rules:"
                self.system_message += rules

            self.system_message += "\n" + finish_prompt         
            new_message=f"current_items={target_items}\n# New challenge: {text}\n"
        else: 
            self.system_message = self.generic_message
            new_message=f"current_items={target_items}\n# New Challenge: {text}\n"

        # new_message=f"# Python\ncurrent_items={items}\n{text}"
        self.add_conversation_message("user", new_message)
        global current_items, to_create_items_list
        current_items = items.copy()
        to_create_items_list=to_create_items_list_param.copy()
        response = self.send_message()
        answer = KubeChatAnswer(response, items)
        answer.sanitize_code_answer()
        # FIXME: remove \n spaces sequences from previos answer ! 
        self.add_conversation_message("assistant", answer.gpt_answer)
        # FIXME: may not be current_items since I no more inject:/
        try:
            answer.items = ast.literal_eval(answer.gpt_answer)
        except Exception as e:
            #FIXME: unclear, find better retry (replay step ?, replay with uncompressed ? try auto fix ?)
            try: 
                exec(answer.gpt_answer, globals())
                # global current_items
                answer.items=globals()['current_items'].copy()
            except:
                exec(self.fix_python_object(answer.gpt_answer), globals())
                # global current_items
                answer.items=globals()['current_items'].copy()
        except:
            #FIXME: unclear, find better retry (replay step ?, replay with uncompressed ? try auto fix ?)
            exec(answer.gpt_answer, globals())
            # global current_items
            answer.items=globals()['current_items'].copy()
        return answer # FIXME : need flatten + merge

    def print_slow(self, str, typing_speed=1200):
        for letter in str:
            print(letter, end="")
            time.sleep(random.random()*10.0/typing_speed)

    def fix_python_object(s):
        """
        This function tries to fix the Python object string by:
        1. Replacing single quotes with double quotes if they are not enclosed within another pair of quotes.
        2. Fixing missing or extra parentheses, brackets, and braces.
        """
        # replace single quotes with double quotes
        s = s.replace("'", '"')
        
        # fix missing or extra brackets
        stack = []
        fixed_s = ''
        for c in s:
            if c in ['(', '[', '{']:
                stack.append(c)
                fixed_s += c
            elif c in [')', ']', '}']:
                if len(stack) == 0:
                    # extra closing bracket, ignore it
                    continue
                last_open = stack.pop()
                if last_open == '(' and c != ')':
                    fixed_s += ')'
                elif last_open == '[' and c != ']':
                    fixed_s += ']'
                elif last_open == '{' and c != '}':
                    fixed_s += '}'
                else:
                    fixed_s += c
            else:
                fixed_s += c
        
        # add missing closing brackets
        while len(stack) > 0:
            last_open = stack.pop()
            if last_open == '(':
                fixed_s += ')'
            elif last_open == '[':
                fixed_s += ']'
            elif last_open == '{':
                fixed_s += '}'
                
        return fixed_s



# Python fix test cases (https://chat.openai.com/share/a75ae33f-9503-444a-ab96-54e4a6d0e1a4)
# test_cases = [
#     "{'key': 'value'}",
#     "{'key': 'value'",
#     "{'key': 'value']}",
#     "{'key': 'value']",
#     "{'key': {'subkey': 'subvalue'}",
#     "{'key': {'subkey': 'subvalue']}",
#     "{'key': {'subkey': 'subvalue']}}",
#     "{'key': [1, 2, 3}",
#     "{'key': [1, 2, 3]}]",
#     "{'key': [1, 2, 3]",
#     "{'key': {'subkey1': 'subvalue1', 'subkey2': ['subvalue2', 'subvalue3']}",
#     "{'key': {'subkey1': 'subvalue1', 'subkey2': ['subvalue2', 'subvalue3']}}",
#     "{'key': {'subkey1': 'subvalue1', 'subkey2': ['subvalue2', 'subvalue3']}",
# ]
