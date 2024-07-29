import functools
import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, HumanMessage
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode
from components.data.models import postgres as PostgresModels
from agent_system.tools import tool_map
from agent_system.agents.account import AccountAgent, AccountTeamAgent
from agent_system.agents.supervisor import SupervisorAgent
from agent_system.agents.reply import ReplyAgent


# agent_names = ["planning_agent", "research_agent", "research_agent"]


def agent_node(state, agent, name):
    result = agent.invoke(state)
    print("node output:", result["output"])
    return {"messages": [AIMessage(content=result["output"], name=name)]}


class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str


class AgentGraph:
    def __init__(
        self,
        bot_team: PostgresModels.BotTeam,
        agent_bots: list[PostgresModels.Bot],
        message_history: list[BaseMessage],
    ):
        self.graph = None
        self.single_agent = None
        self.message_history = message_history

        if len(bot_team.team_members) == 1 and not bot_team.using_supervisor:
            self.single_agent = AccountAgent(bot_data=agent_bots[0], message_history=message_history)
            return

        agent_members = [AccountTeamAgent(bot, message_history) for bot in agent_bots]
        agent_member_names = []
        agent_member_nodes = [
            functools.partial(agent_node, agent=agent_member.agent_chain, name=agent_member.name)
            for agent_member in agent_members
        ]

        self.workflow = StateGraph(AgentState)

        # add graph nodes (supervisor, reply_agent, member nodes)
        for idx, agent in enumerate(agent_members):
            agent_member_names.append(agent.name)
            self.workflow.add_node(agent.name, agent_member_nodes[idx])

        self.supervisor = SupervisorAgent(message_history=message_history, members=agent_member_names)
        self.reply_agent = ReplyAgent()

        self.workflow.add_node("supervisor", self.supervisor.agent_chain)
        self.workflow.add_node("reply_agent", self.reply_agent.agent_chain)

        # all team members route back to supervisor
        for member in agent_member_names:
            self.workflow.add_edge(member, "supervisor")

        conditional_map = {m: m for m in agent_member_names}
        conditional_map["FINISH"] = "reply_agent"

        # supervisor choose member to work
        self.workflow.add_edge(START, "supervisor")
        self.workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
        self.workflow.add_edge("reply_agent", END)

        # check if using general bot
        if bot_team.using_general_bot:
            pass

        self.graph = self.workflow.compile()

    def generate_response(self, user_input: str):
        if self.single_agent is not None:
            return self.single_agent.generate_response(user_input)

        for message in self.graph.stream(
            {"messages": self.message_history[-5:] + [HumanMessage(content=user_input)]}, {"recursion_limit": 10}, debug=True
        ):
            if "reply_agent" in message:
                return message["reply_agent"]["messages"][-1].content
        return "There are some errors with the system. Please try again."


# class AgentState(TypedDict):
#     messages: Annotated[Sequence[BaseMessage], operator.add]
#     sender: str


# def agent_node(state, agent, name):
#     result = agent.agent_chain.invoke(state)
#     # We convert the agent output into a format that is suitable to append to the global state
#     if isinstance(result, ToolMessage):
#         pass
#     else:
#         result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
#     return {
#         "messages": [result],
#         "sender": name,
#     }


# def router(state):  # -> Literal["call_tool", "__end__", "continue"]:
#     # This is the router
#     messages = state["messages"]
#     last_message = messages[-1]
#     if last_message.tool_calls:
#         # The previous agent is invoking a tool
#         return "call_tool"
#     if "FINAL ANSWER" in last_message.content:
#         # Any agent decided the work is done
#         return "__end__"
#     if "GO TO" in last_message.content:
#         agent_name = last_message.content.split(":")[1].strip()
#         if agent_name in agent_names:
#             return f"go_to_{agent_name}"
#     return "continue"


# # class TravelAgentGraph:
# #     def __init__(self):
# #         self.workflow = StateGraph(AgentState)
# #         self.all_tools = []
# #         research_agent = CollaborativeAgent(
# #             PostgresModels.Bot(
# #                 id=0,
# #                 # name=
# #             )
# #         )

# #         research_node = functools.partial(agent_node, agent=research_agent, name="Researcher")

# research_agent = CollaborativeAgent(
#     PostgresModels.Bot(
#         id=0,
#         name="research_agent",
#         conf_instruction="Responsible for searching and validating data related to Vietnamese tourism, ensuring that the information provided is accurate and up-to-date. Whether the Human needs specific details about a destination, cultural insights, historical data, or statistical information, you are here to assist.",
#         conf_model_name="gpt-3.5-turbo-1106",
#         conf_model_temperature=0.5,
#     ),
#     tool_names=["search_google", "search_weather", "scrape_website"],
#     agent_names=agent_names,
# )

# reply_agent = CollaborativeAgent(
#     PostgresModels.Bot(
#         id=0,
#         name="reply_agent",
#         conf_instruction="Responsible for generating human-like text based on the input it receives, ensuring responses are coherent, relevant, and free of language errors. You need to ensure all communication is clear, polite, and helpful. You must also make sure that the information you response to the Human is valid and based on real data (you can ask for other assistants to check it for you). If there is anything that Assistant is not sure about, you will ask the Human for further details. You need to response as the same language as the Human. For example, if Human is talking in Vietnamese, you should reply with Vietnamese also.",
#         conf_model_name="gpt-4-turbo",
#         conf_model_temperature=0.5,
#     ),
#     tool_names=["search_google", "search_weather", "scrape_website"],
#     agent_names=agent_names,
# )

# planning_agent = CollaborativeAgent(
#     PostgresModels.Bot(
#         id=0,
#         name="planning_agent",
#         conf_instruction="Responsible for tasks related to planning tours, visits, food places, and other activities for tourists based on their preferences, duration of stay, location, and number of people. Assistant needs to create well-organized and thoughtful plans, taking into account the Human's preferences and any specific requirements. You can ask the Human for more info, or confirmations about your schedule.",
#         conf_model_name="gpt-3.5-turbo-1106",
#         conf_model_temperature=0.5,
#     ),
#     tool_names=["search_google", "search_weather", "scrape_website"],
#     agent_names=agent_names,
# )


# class TravelAgentGraph:
#     def __init__(self):
#         self.workflow = StateGraph(AgentState)
#         self.tool_node = ToolNode([callable() for callable in tool_map.values()])

#         research_agent_node = functools.partial(agent_node, agent=research_agent, name="research_agent")
#         planning_agent_node = functools.partial(agent_node, agent=planning_agent, name="planning_agent")
#         reply_agent_node = functools.partial(agent_node, agent=reply_agent, name="reply_agent")

#         self.workflow.add_node("research_agent", research_agent_node)
#         self.workflow.add_node("planning_agent", planning_agent_node)
#         self.workflow.add_node("reply_agent", reply_agent_node)
#         self.workflow.add_node("call_tool", self.tool_node)

#         self.workflow.add_conditional_edges(
#             "research_agent",
#             router,
#             {
#                 "continue": "research_agent",
#                 "go_to_reply_agent": "reply_agent",
#                 "go_to_planning_agent": "planning_agent",
#                 "call_tool": "call_tool",
#                 "__end__": END,
#             },
#         )

#         self.workflow.add_conditional_edges(
#             "planning_agent",
#             router,
#             {
#                 "continue": "planning_agent",
#                 "go_to_reply_agent": "reply_agent",
#                 "go_to_research_agent": "research_agent",
#                 "call_tool": "call_tool",
#                 "__end__": END,
#             },
#         )

#         self.workflow.add_conditional_edges(
#             "reply_agent",
#             router,
#             {
#                 "continue": "reply_agent",
#                 "go_to_research_agent": "research_agent",
#                 "go_to_planning_agent": "planning_agent",
#                 "call_tool": "call_tool",
#                 "__end__": END,
#             },
#         )

#         self.workflow.add_conditional_edges(
#             "call_tool",
#             lambda x: x["sender"],
#             {
#                 "research_agent": "research_agent",
#                 "reply_agent": "reply_agent",
#                 "planning_agent": "planning_agent",
#             },
#         )

#         self.workflow.add_edge(START, "reply_agent")


# if __name__ == "__main__":
#     travel_graph = TravelAgentGraph()
#     graph = travel_graph.workflow.compile()

#     # try:
#     #     display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
#     # except Exception:
#     #     # This requires some extra dependencies and is optional
#     #     pass

#     # output = research_agent.agent.invoke("Xin chào")
#     # print(output)

#     events = graph.stream(
#         {
#             "messages": [
#                 HumanMessage(content="Xin chào, có ai ở đây không"),
#                 AIMessage(content="Xin chào! Tôi có thể giúp gì cho bạn?"),
#                 HumanMessage(content="Bạn biết ở Quảng Bình có nơi nào ăn uống ngon không?"),
#             ],
#         },
#         # Maximum number of steps to take in the graph
#         {"recursion_limit": 20},
#     )

#     for s in events:
#         print(s)
#         print("=================")
