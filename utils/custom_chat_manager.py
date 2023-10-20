from autogen import GroupChatManager, GroupChat
from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Union
from autogen import Agent
from autogen import ConversableAgent


# make the selector which selects the speaker the Judge every time
class ManualManager(GroupChatManager):
    def run_andy_chat(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[GroupChat] = None,
    ) -> Union[str, Dict, None]:
        """Run a group chat."""
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        speaker = sender
        groupchat = config
        for i in range(groupchat.max_round):
            # set the name to speaker's name if the role is not function
            if message["role"] != "function":
                message["name"] = speaker.name
            groupchat.messages.append(message)
            # broadcast the message to all agents except the speaker
            for agent in groupchat.agents:
                if agent != speaker:
                    self.send(message, agent, request_reply=False, silent=True)
            if i == groupchat.max_round - 1:
                # the last round
                break
            try:
                # select the next speaker
                speaker = groupchat.select_speaker(
                    speaker, self, groupchat.agent_by_name("Manager"))
                # let the speaker speak
                reply = speaker.generate_reply(sender=self)
            except KeyboardInterrupt:
                # let the admin agent speak if interrupted
                if groupchat.admin_name in groupchat.agent_names:
                    # admin agent is one of the participants
                    speaker = groupchat.agent_by_name(groupchat.admin_name)
                    reply = speaker.generate_reply(sender=self)
                else:
                    # admin agent is not found in the participants
                    raise
            if reply is None:
                break
            # The speaker sends the message without requesting a reply
            speaker.send(reply, self, request_reply=False)
            message = self.last_message(speaker)
        return True, None


# Make the select_speaker call handle Andy the Judge making the call opposed to an openAI call
class ManualGroupChat(GroupChat):
    def select_speaker(self, last_speaker: Agent, selector: ConversableAgent):
        """Select the next speaker."""
        # selector.update_system_message(self.select_speaker_msg())
        # final, name = selector.generate_oai_reply(
        # self.messages
        # + [
        # {
        # "role": "system",
        # "content": f"Read the above conversation. Then select the next role from {self.agent_names} to play. Only return the role.",
        # }
        # ]
        # )

        final = True
        name = input("Who speaks next:")

        if not final:
            # i = self._random.randint(0, len(self._agent_names) - 1)  # randomly pick an id
            return self.next_agent(last_speaker)
        try:
            return self.agent_by_name(name)
        except ValueError:
            return self.next_agent(last_speaker)
