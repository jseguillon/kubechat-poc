# 2nd layer prompt: enrich actions by targeting resources to be transformed
import logging
import time, random
import ast
from .base_commands import KubeCommand, OneShotCommand, KubeChatAnswer

class ActionCommand(OneShotCommand):
    command = '/action'
    description = "Action prompt"
    parameters = []
    command_name='action'
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

    system_message = """Assistant analyze actions and match Kubernetes items.
Example:
{'create': {'user':'create <kindtocreate> for <targetkind> <targetname>'}}

Reply:
{'create': {'user':'create <kindtocreate> for <targetkind> <targetname>', 'to_create_list': [{'kind': '<kindtocreate>', 'namespace': '<kindtocreatens>'}], 'target_list': [{'kind': '<targetkind>', 'name': '<targetname>','namespace': '<targetnamespace>'}]}

Hints: disk is synonym of pvc, autoscaling is ensured via HorizontalPodscaler. Include deployment or statefullset as target when dealing with HorizontalPodscaler, Services, PersitentVolumeClaim, etc... Include Service as target when dealing with Ingress, etc...

Items in lists can only support 3 fields: kind, name, and namespace: no spec, no metadata.

Now reply no comment, nor note, nor explanation but only pure Python:
"""
