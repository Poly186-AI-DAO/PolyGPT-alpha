import json
from typing import Any

from utils.poly_logger import PolyLogger

LOG = PolyLogger(__name__)

class PolyAutogenReact :
    """Handles reactions to method calls."""

    def __init__(self, agent, database, workspace):
        self.agent = agent
        self.database = database
        self.workspace = workspace
        LOG.info(f"🔔 {self.agent.name}: Reaction class initialized.")

    def _log_with_task_step(self, agent_name, message, data):
        task_id = data.get('current_task_id') if data else None
        step_id = data.get('current_step_id') if data else None
        # LOG.info(f"🔔 {agent_name} [Task: {task_id}, Step: {step_id}]: {message}")

    def save_to_db_on_receive(self, data):
        # Assuming data contains task_id and the message received
        task_id = data.get('current_task_id')
        message = data.get('message')
        if task_id and message:
            # Create a new step with the message as input
            step_input = {"input": message}
            self.database.create_step(task_id, step_input)
            # LOG.info(f"🔔 {self.agent.name} [Task: {task_id}]: Message received and saved to database.")
        # else:
            # LOG.warning(f"⚠️ {self.agent.name} [Task: {task_id}]: Failed to save received message to database. Task ID or message missing.")

    def save_to_db_on_run_code(self, data):
        # Assuming data contains task_id and the code executed
        task_id = data.get('current_task_id')
        code = data.get('code')
        if task_id and code:
            # Create a new artifact with the code as a file_name (or any other relevant attribute)
            self.database.create_artifact(task_id, file_name=code, relative_path="code_executed")
            LOG.info(f"🔔 {self.agent.name} [Task: {task_id}]: Executed code saved to database.")
        else:
            LOG.warning(f"⚠️ {self.agent.name} [Task: {task_id}]: Failed to save executed code to database. Task ID or code missing.")

    def save_to_workspace(self, task_id: str, path: str, data: Any):
        # First, we'll attempt to serialize the data to a JSON string
        try:
            data_str = json.dumps(data, default=str)
            data_bytes = data_str.encode('utf-8')
        except TypeError as e:
            LOG.error(f"Failed to serialize data to JSON: {e}")
            return

        # Attempt to save the serialized data to the workspace
        try:
            self.workspace.write(task_id, path, data_bytes)
            LOG.info(f"Successfully saved data to workspace for task {task_id} at path {path}")
        except Exception as e:
            LOG.error(f"Error saving data to workspace: {e}")

    def react(self, method_name: str, data: Any = None):
        """React based on the method that was called."""
        self._log_with_task_step(self.agent.name, f"Reacting to method: {method_name}.", data)
        reaction_method = getattr(self, f"on_{method_name}", self.default_reaction)
        self._log_with_task_step(self.agent.name, f"Found reaction method: {reaction_method.__name__}.", data)
        reaction_method(self.agent, data)
        self._log_with_task_step(self.agent.name, "Reaction method executed.", data)

    def default_reaction(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "No reaction defined for this method.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'default_reaction_data.json', data)

    def on__append_oai_message(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected an _append_oai_message call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], '_append_oai_message_data.json', data)

    def on__process_received_message(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a _process_received_message call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], '_process_received_message_data.json', data)

    def on__print_received_message(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a _print_received_message call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], '_print_received_message_data.json', data)

    def on__match_trigger(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a _match_trigger call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], '_match_trigger_data.json', data)

    def on_run_code(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a run_code call! Reacting accordingly.", data)
        self._log_with_task_step(agent.name, "Attempting to save executed code to database.", data)
        self.save_to_db_on_run_code(data)
        self._log_with_task_step(agent.name, "Executed code has been saved to database.", data)

    def on__format_json_str(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a _format_json_str call! Reacting accordingly.", data)

    def on_send(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a send call! Reacting accordingly.", data)

    def on_receive(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a receive call! Reacting accordingly.", data)
        self._log_with_task_step(agent.name, "Attempting to save received data to database.", data)
        self.save_to_db_on_receive(data)
        self._log_with_task_step(agent.name, "Received data has been saved to database.", data)

    def on_initiate_chat(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected an initiate_chat call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'initiate_chat_data.json', data)

    def on_register_reply(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a register_reply call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'register_reply_data.json', data)

    def on_generate_reply(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a generate_reply call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'generate_reply_data.json', data)

    def on_execute_code_blocks(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected an execute_code_blocks call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'execute_code_blocks_data.json', data)

    def on_execute_function(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected an execute_function call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'execute_function_data.json', data)

    def on_generate_init_message(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a generate_init_message call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'generate_init_message_data.json', data)

    def on_register_function(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Detected a register_function call! Reacting accordingly.", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'register_function_data.json', data)

    def on_get_human_input(self, agent, data: Any = None):
        self._log_with_task_step(agent.name, "Waiting for human input...", data)
        if data and 'current_task_id' in data:
            self.save_to_workspace(data['current_task_id'], 'get_human_input_data.json', data)
