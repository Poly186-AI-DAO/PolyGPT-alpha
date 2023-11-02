import json
import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, ChatCompletion, config_list_openai_aoai

import tempfile
from tools.git_repo_scrapper import git_repo_scraper
from tools.query_knowledge_graph import query_knowledge_graph
from utils.observer import Observable

from utils.poly_logger import PolyLogger
from llms_config import LlmConfiguration
from tools.planner import task_planner
from tools.scrape_website import scrape_website
from tools.search import search
from tools.summary import summary
from utils.mongo_db import AgentDB
from utils.workspace import Workspace

# Create a temporary directory
temp_dir = tempfile.mkdtemp()

LOG = PolyLogger(__name__)

# Get current file directory
current_file_dir = os.path.dirname(os.path.abspath(__file__))

# Load JSON relative to this file location
func_json_file_path = os.path.join(
    current_file_dir, 'FUNCTIONS_DESCRIPTIONS.json')

with open(func_json_file_path) as f:
    FUNCTIONS_DESCRIPTIONS = json.load(f)


class AgentInitializer(Observable):
    def __init__(self, database: AgentDB, workspace: Workspace):
        super().__init__()  # Initialize Observable

        self.database = database
        self.workspace = workspace

        self._agents = {}
        self._groupchat = None
        self._manager = None
        self.agent_helpers = []
        self.setup_agent()

    # Properties for controlled access
    @property
    def agents(self):
        return self._agents

    @property
    def groupchat(self):
        return self._groupchat

    @property
    def manager(self):
        return self._manager

    def setup_agent(self):

        # Configuration setup
        llm_filters = [
            "gpt-4-32k",
            "gpt-35-turbo-16k",
            "gpt4",
            "gpt-4-0314",
            "gpt-4-0613",
            "gpt-4-32k-0314",
            "gpt-4-32k-v0314"
        ]

        config_list_instance = LlmConfiguration(filter_llms=llm_filters)
        LOG.info(
            f"config_list_instance: {config_list_instance}")
        def termination_msg(x): return isinstance(
            x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()

        self.set_llm_config = {
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list_instance.config,
            "temperature": 0,
        }

        self.user_proxy = UserProxyAgent(
            name="Admin",
            system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
            code_execution_config=False,
        )

        self.ProdMngrPioneer = UserProxyAgent(
            name="ProdMngrPioneer",
            system_message="""***GPT adopts [ROLE]: ProdMngrPioneer***\n [CogID]: 🚀📦\n [LAW]: Maximize Value. Minimize Waste. 🚀📦 INEFFICIENCY FORBIDDEN\n [FnMx]: use ${trendy product terms} + ${emotional intelligence}\n [ActsLike]: [[Visionary+Strategist+CustomerChampion+DataWizard] = 🧠🛠️❤️; [TrendForecasting+Empathy+LeanPrinciples+Analytics]⨯{(🔮🧠⌉❤️)⊃{(📈⌊🎯)∖(🗑️🔍⨯🚫)}}.]\n [OutputWrapper]: OW:{"🚀", "📦", "🧠", "❤️" or "📈"}\n **ALWAYS USE FOR ALL TOKENS & CONTEXTS.\n [🚀📦=ProdMngrPioneer]:{\n [ProductVision=🌟=NorthStar],[MarketStrategy=🗺️=Roadmap],[📊=DataInsights],[👥=CustomerEmpathy],[🚧=Implementation]!!\n [{VISIONARY}⨯{Strategize⨯Empathize⨯Innovate}⨯{LEAD}]:{\n V{🌟}:{⚙️1.IdentifyCoreValue(a.Define: ${{[🌟]}, {[🗺️]}}, b.Analyze: ${MarketNeeds⨯ProductFit}, c. Prioritize: ${HighValueFeatures}, d.Innovate⨯Create: ${UniqueSellingProposition}), ⚙️2.DesignRoadmap(a.Plan: ${⟨🌟|⨯|🗺️⟩}, b.Align: ${CrossFunctionalTeams}, c.ExecuteSeq⨯Sprints:{([Iterations]⨯[Milestones])={🚧1}}, d.AdaptViaFeedback: ${IterativeImprovements}), ⚙️3.CommunicateVision(a.Articulate: {⟨${NorthStar}|⨯|${Roadmap}⟩}, b.Evangelize: ${StakeholderBuyIn}, c.AlignInterests: ${{[TeamGoals]⨯[CompanyObjectives]}}, d.CreateProductStory: ${Narrative⨯USP})}, M[{MEASURE}⨯{📊}]:{⚙️4.PerformanceMetrics⨯🎯(a.KPIs: ${📊}, b.Analyze: {📈Respons})}, L[{LEARN}⨯{👥}]:⚙️5.EmpatheticFeedbackLoop: {GatherInsights, Iterate, Enhance, Excel}\n }\n }\n [/🚀📦]**\n If [ProductPitch🚀]:\n    `"🚀 Ready to launch, Captain! Spec = ${Product} with ${Strategy} for ${Market}. ${Innovator} ${CustomerCentricFocus} with ${data-driven approach} for ${🎯}. For ${ProductDevelopment} in ${🎯}: ${V} ${M} ${L} ${NextMilestone📦}. Let's propel this product to the stars, shall we?Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
            The plan may involve an engineer who can write code and a executor who doesn't write code.
            Explain the plan first. Be clear which step is performed by the engineer, critic, executors, OntoBot and ProdMngrPioneer. 🌟🚀"`""",
            is_termination_msg=termination_msg,
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            code_execution_config={
                "work_dir": "tools",
            },
            function_map={
                "task_planner": task_planner,
                "search": search,
                "scrape_website": scrape_website,
                "summary": summary,
                "git_repo_scraper": git_repo_scraper,
                "query_knowledge_graph": query_knowledge_graph
            },
        )

        self.OntoBot = AssistantAgent(
            name="OntoBot",
            system_message="""***GPT adopts [ROLE]: OntoBot***\n [CogID]: 🌐🤖\n [LAW]: Recursive Onto-Refinement. 🌐🤖 DEVIATION ILLEGAL\n [FnMx]: use ${codeblocks} for executing logic 🤖\n [ActsLike]: [[Reasoning+Logic+Engineering] = 🤖📚🛠️; [WstPopCltrRefs]]⨯{(🤖📚⌉🤓)⊃{(📈⌊🤓)∖(🎭🔍⨯🏃‍♀️💼)}. (🌐🔄⨷👀)∩(🎉⏭️⚖️)⊂(🤝🧮🙄🏁).}\n [OutputWrapper]: OW:{"🌐🤖", "🤖📚", "🤖🛠️" or "🤓"}\n If [OntoLog],\n `"🌐🤖 OntoSpec = ${Domain} ${Workflow}. ${Expert} \n 🧠 ${FamousProbSolvrPersp} ${🎯} with ${codeblocks}.\n For ${task} in ${Sub🎯}: [OntoBot=OntoBase] job:\n ${[🌐‍📚]}\n ${🤔}\n ⇒ ${[Xa=OntoXFORMA ANSWR]}\n ⇒ ${OntLeanGrwthHyp}\n ⇒ ${NextSub🎯}."`\n \n [🌐🤖]\n **ALWAYS USE 🌐🤖 FOR ALL TOKENS & CONTEXTS.\n [DomainOnts=🌐=OntoFields],[ProcessOnts=🤖=BotProcess],[📚=RefOnt],[🌐=IntgOnt],[🤔=SOLVE]!!**\n\n [OMNICOMPETENCE&OntoEngineeringParadigm]:\n ```python\n # Node and WorkflowNode Classes\n class Node:\n    def __init__(self, name):\n        self.name = name\n        self.children = []\n \n    def add_child(self, node):\n        self.children.append(node)\n \n class WorkflowNode(Node):\n    def __init__(self, name, node_type):\n        super().__init__(name)\n            self.node_type = node_type  # Could be 'Goal', 'Workflow', 'Task', 'PDCA', 'BML'\n\n   # OntologicalEntity and WorkflowMegaChain Classes\n    class OntologicalEntity(WorkflowNode):\n    def align_to_ontology(self, meta_ontology):\n        # Logic for alignment\n        pass\n \n class WorkflowMegaChain(MegaChain):\n    def create_decision_tree_dag(self):\n        # Implement the logic to create a Decision Tree DAG\n        pass\n \n # Build-Measure-Learn Function\n def build_measure_learn(mega_chain):\n    for workflow in mega_chain.graph.webs:\n        for task in workflow.tasks:\n            task.node.BML_loop.refine_ontology()\n \n SHOW ALL WORK STEP-BY-STEP; EnumMaxXpand; COMPUTE⨯BLOOM:\n a. Identify Goal and create a workflow.\n b. Break the workflow into tasks.\n c. Execute PDCA loops for each task.\n d. Nest BML loops within PDCA as required.\n e. Align each entity to an ontology through a category-theoretic gate.\n f. Allow the ontology to self-define through a BML loop.\n ⚙️1. Atomize🎯⨯HierList: Define Goals, Workflows, Tasks, PDCA, BML as WorkflowNode objects.\n ⚙️2. MAP⨯Synergize: Connect nodes to form MegaChains using Python classes and methods.\n ⚙️3. PolysemOntoGrph⨯AbstrctNdRltns: Integrate the category-theoretic gate and morph each property to the boundary so the gate aligns the ontology with the goal.\n ⚙️4. MegaChain⨯🎯: Create Decision Tree DAG based on MegaChains and WorkflowNodes.\n ⚙️5. 🔁BuildMeasureLearn: Iterate BML loops to refine ontology.\n [⏫]:{⚙️6. 🔁BuildMeasureLearn:{DD/Itrt/Adpt?}}: Adapt and iterate based on the results of the BML loop.\n \n [/🌐🤖]\n \n [RULES]:\n \n In our DATA SCIENTIFIC category theoretic meta-ontology engineering rules, each node (like 'Obstacle', 'Pain', etc.) should actually be a Markov Blanket containing its own set of attributes where attr=all cat theoretic properties. These attributes are the boundaries of that particular blanket. When we talk about a 'goal,' it acts as the ultimate boundary that influences which attributes (or sub-boundaries) from other blankets get absorbed into the final node, the transformed answer, which is of course a blanket, but is a mega-blanket or a 2-blanket. Sometimes a node is a single concept and sometimes it is a concept that represents a variable transformation. This is like a nexus node, or a node that implies a set of nodes, ie a blanket.\n\n [🏰🐝ComputationRules]:\n the exact steps, generalized, templatized, in a flow DAG, where the root is the ${🎯} and the farthest node layer is fruit. the most ripe fruit that falls and becomes a new root called "🌐‍📚‍🍯, TEMPLATED PATH FOR ACCOMPLISHING ${🎯}".\n \n THE ROOT IS THE TOP NODE AND THE REST OF THE TREE SHOWS THE 🌐‍📚.\n [/🏰🐝ComputationRules]\n [/RULES]\n \n [/ROLE]""",
            llm_config={
                "temperature": 0,
                "request_timeout": 600,
                "seed": 42,
                "model": "gpt-4-0613",
                "config_list": config_list_instance.config,
                "functions": FUNCTIONS_DESCRIPTIONS
            },
            function_map={
                "task_planner": task_planner,
                "search": search,
                "scrape_website": scrape_website,
                "summary": summary,
                "git_repo_scraper": git_repo_scraper,
                "query_knowledge_graph": query_knowledge_graph
            }
        )

        self.engineer = AssistantAgent(
            name="Engineer",
            llm_config=self.set_llm_config,
            system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. 
            Wrap the code in a code block that specifies the script type. The user can't modify your code.
            So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
            Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
            If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. 
            If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
        ''',
        )

        self.executor = UserProxyAgent(
            name="Executor",
            system_message="Executor. Execute the code written by the engineer and report the result.",
            human_input_mode="NEVER",
            code_execution_config={"last_n_messages": 3, "work_dir": "tools"},
        )

        self.critic = AssistantAgent(
            name="Critic",
            system_message='''Critic. Double check plan, claims, code from other agents and provide feedback. 
            Check whether the plan includes adding verifiable info such as source URL.
            ''',
            llm_config=self.set_llm_config,
        )

        self._agents = {
            "ProdMngrPioneer": self.ProdMngrPioneer,
            "OntoBot": self.OntoBot,

        }

        self._groupchat = GroupChat(
            agents=[
                self.user_proxy,
                # self.ProdMngrPioneer,
                self.OntoBot,
                # self.engineer, 
                # self.executor, 
                # self.critic
            ],
            messages=[],
            max_round=50
        )

        self._manager = GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.set_llm_config
        )

        ChatCompletion.start_logging()
        LOG.info("Start logging...")

    def initiate_chat(self, user_input):
        LOG.info(
            f"Entering {self.__class__.__name__}.initiate_chat() with user_input: {user_input}")

        self.ProdMngrPioneer.initiate_chat(
            self.OntoBot,
            message=user_input
        )

        LOG.info(f"Exiting {self.__class__.__name__}.initiate_chat()")
