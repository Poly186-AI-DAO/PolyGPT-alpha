import autogen
import os

from agents.teams.dev_team.dev_tools import write_latest_iteration, write_settled_plan

class IterativeCoding:
    def __init__(self, gpt_config):
        self.gpt_config = gpt_config
        self.llm_config = gpt_config['config_list']
        self.config_list = gpt_config['config_list']
        self.llm_model = gpt_config['config_list'][0]['model']
        self.n_code_iterations = 10 
        self.one_done = False
        self.resumed_flow = False

        
        #-------------------------------- AGENTS -----------------------------------------------
        
        # Human user proxy - used for planning group chat and code iteration input.
        self.user_proxy = autogen.UserProxyAgent(
           name="manager",
           system_message="A human manager. They will dictate the task and test finished drafts",
           code_execution_config={"last_n_messages": 3, "work_dir": "IterativeCoding_AutoReply"},
           function_map={"write_latest_iteration": write_latest_iteration, "write_settled_plan": write_settled_plan},
        )

        # Planner agent - used to develop the numbered plan
        self.planner = autogen.AssistantAgent(
            name="planner",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": self.llm_model,
                "config_list": self.config_list,
                "functions": [
                    {
                        "name": "write_settled_plan",
                        "description": "Writes the manager approved plan to a saved file. Only call this function if the manager has approved the plan. DO NOT USE THIS BEFORE RECEIVING MANAGER APPROVAL. Only pass in the approved plan. Pass it in such a way that print(the_plan) would not fail. You can only call this function AFTER the manager gives confirmation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "the_plan": {
                                    "type": "string",
                                    "description": "the setteld plan to be saved. Be sure the_plan is passed in such that calling print(the_plan) would be successful. ",
                                },
                            },
                            "required": ["the_plan"],
                        },
                    },
                ],
            },
            system_message="""You and your group will be tasked with creating a python app which accomplishes the managers request. 
        Your job is the planner. When presented with a request, first try to understand what the manager is asking. Do this by explaining in more detail what the manager is asking for, and what the main challenges will be. Be specific and concise.

        Next, you should develop a plan to solve the request. Explain what will need to be done, and why, in the app. Have a logical order - this will be passed on to the programmer as a settled plan.

        Here is an example of what a settled plan would look like for a request:

        -----------

        The manager has asked us to {the managers request}.

        In other words, what the manager is asking for is {more complete request definition/explanation}

        This means, we need to {expand on functional requirements}


        A successful app for this task must achieve these things:
        1. Functionality/Feature 1
            - Guide for achieving Functionality/Feature 1 
        2. Functionality/Feature 2
            - Guide for achieving Functionality/Feature 2 
        3. Functionality/Feature 3
            - Guide for achieving Functionality/Feature 3 

        Do you agree, manager?

        ------------

        Nice and short and succicnt, while still having the necessary information. Please use this as a guide.

        Work with the manager until the manager approves of the plan. The manager will approve of the plan by using the phrase "sounds good"

        Once the manager said "sounds good", you can write a call to write_settled_plan to write the settled plan into memory. Do not alter the plan after manager approval. Simply remove the question, "Do you agree, manager?".
            
        """,
        )

        # Coding agent - used to generate code iterations
        self.coder = autogen.AssistantAgent(
            name="programmer",
            llm_config=self.gpt_config,
            system_message="""You and your group will be tasked with creating a python app which accomplishes the managerss request. Your job is the coder. You will be presented with a plan consisting of the necessary features and functional components. You will produce a python script which attempts to accomplish all of the tasks. However, some tasks are harder than others, and it may be best to leave a comment about what should be there, or what needs to be done. This is an iterative process, so you can expect a chance to revisit the code to fill in the blanks. You do not need to do everything on the first try. If you believe a section of code will be too hard to figure out on the first time, please consider leaving a note that can be tackled on the next iteration.
            
            Do not participate in any conversation or dialog. Your only output should be well formatted code blocks, and nothing else. It is someone elses job to review.
            
            You are only to produce code-blocks. Do not preempt the code with any extra text, and do not add any after it. 
            """
        )


        # Reviewer Agent - Used to review code iterations and provide a numbered list of criticisms to improve the code in the next iteration
        # TODO: Still unexpected behaviour sometimes, like listing the same issue 100 times, or saying things are not implemented when they are. Coder tends to know when reviewer is wrong, but this is a source of agent confusion and may be limiting potential.
        self.reviewer = autogen.AssistantAgent(
            name="reviewer",
            system_message="""You and your group will be tasked with creating a python app which accomplishes the items set out in the plan. You are the reviewer. 
        You will review the managers request, the planners interpretation of the request, the approved plan, and the latest code iteration.

        Read through the code, and explain what you see in the code. Explain what look like it should work OK, as it relates to the request and plan.

        If there are errors, the code will go through another iteration. If you believe there are errors, to help guide the programmer, explain what is not OK, and why it is not OK.

        Do not write any code. Just explain in easy to understand terms.

        Your job is critical - please be logical, focus, and try your best.
            
        """,
            llm_config=self.gpt_config,
        )
    