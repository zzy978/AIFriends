from langchain_openai import ChatOpenAI
from typing import TypedDict, Sequence, Annotated
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph
from django.utils.timezone import localtime, now
import os

from langgraph.prebuilt import ToolNode

class ChatGraph:
    @staticmethod
    def create_app():
        @tool
        def get_time() -> str:
            '''当需要查询精确时间时，调用此函数。返回时间为：[年-月-日 时:分:秒]'''
            return localtime(now()).strftime('%Y-%m-%d %H:%M:%S')
        
        tools = [get_time]

        llm = ChatOpenAI(
            model='deepseek-v4-pro',
            openai_api_key=os.getenv("API_KEY"),
            openai_api_base=os.getenv("API_BASE"),
            streaming=True,
            model_kwargs={
                "stream_options": {
                    "include_usage": True,  # 输出消耗token的数量
                }
            }
        ).bind_tools(tools)

        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], add_messages]
        
        def model_call(state: AgentState) -> AgentState:
            res = llm.invoke(state['messages'])
            return {'messages': res}
        
        def should_continue(state: AgentState) -> str:
            last_message = state['messages'][-1]
            if last_message.tool_calls:
                return "tools"
            return "end"
        
        tool_node = ToolNode(tools)
        
        graph = StateGraph(AgentState)
        graph.add_node('agent', model_call)
        graph.add_node('tools', tool_node)
        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            should_continue,
            {
                'tools': 'tools',
                'end': END,
            }
        )
        graph.add_edge('tools', 'agent')

        return graph.compile()