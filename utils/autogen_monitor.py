import asyncio
import functools

from utils.observer import Observable
from utils.poly_logger import PolyLogger



LOG = PolyLogger(__name__)

"""
The AutogenAgentHelper class is a utility for monitoring and logging various method calls of an agent.
It's a form of Aspect-Oriented Programming (AOP) where certain methods of interest are wrapped with 
additional functionality (in this case, logging) without altering the core logic of those methods. 
This can be very powerful for debugging, metrics collection, or other cross-cutting concerns.
"""


class AutogenMonitor(Observable):
    def __init__(self, agent, polygpt_agents, groupchat, manager, methods_to_monitor=None):
        super().__init__()  # Call the __init__ method of Observable

        self.agent = agent
        self.polygpt_agents = polygpt_agents
        self.groupchat = groupchat
        self.manager = manager
        self.method_wrappers = set()

        # Use provided methods to monitor or default to the property
        if methods_to_monitor is None:
            methods_to_monitor = self.default_monitored_methods
        self.monitor_agent(methods_to_monitor)

        LOG.info(f"AutogenAgentHelper initialized for agent {agent.name}.")

    @property
    def default_monitored_methods(self):
        return [
            "_append_oai_message",
            "_process_received_message",
            "_print_received_message",
            "_match_trigger",
            "get_human_input",
            "run_code",
            "_format_json_str",
            "send",
            "receive",
            "initiate_chat",
            "register_reply",
            "generate_reply",
            "execute_code_blocks",
            "execute_function",
            "generate_init_message",
            "register_function"
        ]

    def monitor_agent(self, methods_to_monitor):
        for method_name in methods_to_monitor:
            if hasattr(self.agent, method_name) and method_name not in self.method_wrappers:  # Corrected this line
                method = getattr(self.agent, method_name)
                wrapped_method = self.wrap_agent_method(method)
                setattr(self.agent, method_name, wrapped_method)
                self.method_wrappers.add(method_name)  # Corrected this line
            else:
                LOG.warning(
                    f"🚨 {self.agent.name}: METHOD {method_name} NOT FOUND or already wrapped")

    def wrap_agent_method(self, func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self.register_method_call(func, args, kwargs)
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self.register_method_call(func, args, kwargs)
                return func(*args, **kwargs)
            return sync_wrapper

    def register_method_call(self, func, args, kwargs):
        # Add the agent's name to the data
        data_with_agent_name = {'agent_name': self.agent.name, 'data': (args, kwargs)}
        # Schedule the asynchronous notify function to run
        self.notify(func.__name__, data_with_agent_name)  # Use the enhanced data

        for arg in args:
            self.log_method_detail("ARGUMENT", arg)
        for key, value in kwargs.items():
            self.log_method_detail(f"KWARG {key}", value)

    def log_method_detail(self, detail_type, value):
        try:
            LOG.info(
                f"🔎 {self.agent.name}: DETAIL - {detail_type} TYPE: {type(value)} VALUE: {value}")
        except Exception as e:
            LOG.warning(
                f"🚧 {self.agent.name}: Could not log {detail_type.lower()} detail: {e}")

    async def notify(self, event, data):
        LOG.info(
            f"🔔 {self.agent.name}: NOTIFYING THE OCCURRENCE OF THIS EVENT: {event} AND DATA: {data}")
        await super().notify_observers_async(event=event, data=data)
        LOG.info(f"🔔 {self.agent.name}: NOTIFICATION SENT")
