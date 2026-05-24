from pprint import pprint

from web.models.friend import Message, SystemPrompt
from web.views.friend.message.memory.graph import MemoryGraph
from langchain_core.messages import HumanMessage, SystemMessage
from django.utils.timezone import localtime, now

def create_system_message():
    system_prompt = SystemPrompt.objects.filter(title='记忆').order_by('order_number')
    prompt = ''
    for sp in system_prompt:
        prompt += sp.prompt
    return SystemMessage(prompt)
def create_human_message(friend):
    prompt = f'【原始记忆】\n{friend.memory}\n'
    prompt += f'【最近对话】\n'
    messages = list(Message.objects.filter(friend=friend).order_by('-id')[:10])
    messages.reverse()
    for m in messages:
        prompt += f'user: {m.user_message}\n'
        prompt += f'AI: {m.output}\n'
    return HumanMessage(prompt)

def update_memory(friend):
    app = MemoryGraph.create_app()

    inputs = {
        'messages': [
            create_system_message(),
            create_human_message(friend),
        ]
    }
    pprint(inputs)
    res = app.invoke(inputs)
    friend.memory = res['messages'][-1].content
    pprint(friend.memory)
    
    friend.update_time = now()
    friend.save()