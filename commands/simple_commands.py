import logging
from .base_commands import  KubeCommand, OneShotCommand, KubeChatAnswer

class  ChatCommand(KubeCommand):
    description = "Default chat prompt"
    parameters = [ ]
    command = "/chat"
    model="gpt-3.5-turbo"
    stream = True
    include_items = True
    sanitize_code_answer = False
    openai_params = {
        'temperature': 0,
        'max_tokens': 3000,
        'request_timeout': 60,
        'stream': stream
    }

    system_message = """Kubernetes AI bot, you fake you manage a Kubernetes cluster and create/maintain YAML content.
Example: 
- "how to deploy php": you explain YAMLs and finish with "next step: do you want me to create <yamls> for you ?"

Note: you don't use helm.

Answer:"""

    def new_message(self, text, items, **user_params):
        logging.debug(f'New message {self.command} - {self.model} with text: {text}, params: {user_params} and files: {items}')

        new_message=f"Knowing list of Kubernetes YAML you, the assistant, just created: current_items={items}\n {text}"
        
        self.add_conversation_message("user", new_message)
        response = self.send_message()
        answer = KubeChatAnswer(response, items)

        if self.sanitize_code_answer: answer.sanitize_code_answer()

        self.add_conversation_message("assistant", answer.gpt_answer)
        self.save_messages()
        return answer

class IntentCommand(KubeCommand):
    command = ''
    description = ""
    parameters = [ ]


class TransformCommand(OneShotCommand):
    command = ''
    description = ""
    parameters = [ ]
    system_message = """You are a Kubernetes expert and help me manipulate a variable named 'current_items' which reflects the state of a cluster.
You output python script that transforms current_items to reflect new desired cluster status. You cant add comments nor explanations. You cant' reply in code block form. Only python.
You cant redefine 'current_items='. You can append and del to manipulate current_items.
If intent is non obvious, please refer to provided Intent.
Hint: any new item should be in the form of:
- {'apiVersion': '<apiversion>', 'kind': '<kind>', 'metadata': {'name': '<name>', namespace:'<optional namespace>'}

Take care of not creating infinite loop !
"""

class ParallelCommand( KubeCommand):
    def __init__(self, sub_prompts):
        super().__init__()
        self.sub_prompts = sub_prompts

    async def new_message(self, text, file_list, **user_params):
        self.add_conversation_message("user", text)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            tasks = [loop.run_in_executor(executor, sub_prompt.new_message, text, file_list, **user_params) for sub_prompt in self.sub_prompts]
            results = await asyncio.gather(*tasks)

        combined_answer = " ".join([result.gpt_answer for result in results])
        self.add_conversation_message("assistant", combined_answer)
        return  KubeChatAnswer(combined_answer, file_list)

class ParallelSubCommand1(OneShotCommand):
    description = "Parallel Sub-prompt 1"
    command = "/parallel_sub_prompt1"

class ParallelSubCommand2(OneShotCommand):
    description = "Parallel Sub-prompt 2"
    command = "/parallel_sub_prompt2"
