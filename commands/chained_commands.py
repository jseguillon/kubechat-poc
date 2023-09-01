from .base_commands import ChainedCommand,  KubeCommand

class ChainedCommand1(ChainedCommand):
    command = '/chained'
    description = "Chained prompt"
    parameters = []

    def __init__(self):
        sub_prompts = [HelloChained1(), HelloChained2()]
        super().__init__(sub_prompts)

class HelloChained1( KubeCommand):
    system_message = "Say 'Hello, Chained!'"
    
class HelloChained2( KubeCommand):
    system_message = "Say 'Hello, Chained 2!'"
