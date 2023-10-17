
import os

def read_text_file(self, file_path):
        # Implement your file reading logic here
        try:
            with open(file_path, 'r') as file:
                contents = file.read()
            return contents
        except FileNotFoundError:
            print("File not found.")
        except IOError:
            print("Error reading file.")

def write_latest_iteration_manual(self, code_message):
        # Implement writing the latest iteration manually here
        if code_message[0] == '`':
            # remove code block formatting
            code_message = code_message.replace('`','')
            
            # remove python from start of code
            code_message = code_message[6:]
            
            self.write_latest_iteration(code_message)
        
        else:
            self.write_latest_iteration(code_message)

def write_latest_iteration_comments(self, comment):
        # Implement writing the latest iteration comments here
        script_name = self.working_dir+"comments_v1.log"
        version = 1

        while os.path.exists(script_name):
            version += 1
            script_name = f"{self.working_dir}/comments_v{version}.log"

        with open(script_name, "w") as script_file:
            script_file.write(comment)

def retrieve_latest_iteration(self):
        # Implement logic to retrieve the latest iteration here
        files = os.listdir(self.working_dir)
        py_files = [file for file in files if file.endswith('.py')]
        version_numbers = []
        for file in py_files:
            version = file.split('_v')[-1].split('.py')[0]
            version_numbers.append(int(version))
        max_version = max(version_numbers)
        for file in py_files:
            if file.endswith(f'_v{max_version}.py'):
                return file
        return None
        
    # Write latest python code iteration to an automatically incrementing script file.
def write_latest_iteration(self, code_block):
        script_name = self.working_dir+"script_v1.py"
        version = 1

        while os.path.exists(script_name):
            version += 1
            script_name = f"{self.working_dir}/script_v{version}.py"

        with open(script_name, "w") as script_file:
            script_file.write(code_block)
            
    # write the settled plan to a master plan text file      
def write_settled_plan(self, the_plan):
        plan_name = self.working_dir+"MasterPlan.txt"


        with open(plan_name, "w") as plan_file:
            plan_file.write(the_plan)
            
def list_subdirectories(self,directory):
        subdirectories = []
        if os.path.exists(directory) and os.path.isdir(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    subdirectories.append(item)
        return subdirectories
    
    # Set project directory, must be passed in with trailing slash eg. "pdir/"
def setProjectDir(self,project_dir):
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        self.project_dir = project_dir
        
    # Check if a version 1 file has already been generated      
def does_version_one_exist(self):
        plan_name = self.working_dir+"comments_v1.log"
        if os.path.exists(plan_name):
            return True
        else:
            return False
            
    # Retrieve the highest-number version comment iteration   
def retrieve_latest_iteration_comment(self,):
        files = os.listdir(self.working_dir)
        py_files = [file for file in files if file.endswith('.log')]
        version_numbers = []
        for file in py_files:
            version = file.split('_v')[-1].split('.log')[0]
            version_numbers.append(int(version))
        max_version = max(version_numbers)
        for file in py_files:
            if file.endswith(f'_v{max_version}.log'):
                return file
        return None

def run(self):
        
        found_dirs = self.list_subdirectories(self.project_dir)

        # No previously found projects
        if len(found_dirs) == 0:
            # Start new project
            print("No previous projects found! Starting a new project...")
            self.manager_request = input("Welcome to Iterative Coding! What python creation would you like? Type below:\n")
            self.project_name = input("What name would you like to give this project? Type below (must follow directory naming rules):\n")
            
            self.working_dir =  self.project_dir + self.project_name + "/"
            os.makedirs(self.working_dir)
            self.resumed_flow = False
            
        else:
            # handle new or old project
            user_selection = input("Welcome to Iterative Coding! Would you like to:\n1. Start a new project. \n2. Continue an old project.\n\nSelection:")
            
            if int(user_selection[0]) == 1:
                # Start a new Project
                manager_request = input("Welcome to Iterative Coding! What python creation would you like? Type below:\n")
                project_name = input("What name would you like to give this project? Type below (must follow directory naming rules):\n")
                
                self.manager_request = manager_request
                self.project_name = project_name  
                self.working_dir =  self.project_dir + self.project_name + "/"
                os.makedirs(self.working_dir)
                self.resumed_flow = False
                
            elif int(user_selection[0]) == 2:
                # list old projects
                print("\nThe following project folders were found:\n")
                
                for i in range(len(found_dirs)):
                    print("{sel}. {pdir}".format(sel = i, pdir = found_dirs[i]))
                    
                p_num = int(input("\nSelect project to continue:")[0])
                
                self.project_name = found_dirs[p_num] 
                self.working_dir =  self.project_dir + self.project_name + "/"
                self.one_done = self.does_version_one_exist()
                self.resumed_flow = True
                
        
  
        # If this is a first-time flow
        if not self.resumed_flow:
            self.user_proxy.initiate_chat(
                self.planner,
                message=self.manager_request,
            )
            # exit()

        # Begin the code iteration cycle
        for i in range(self.n_code_iterations):
            # First cycle of iterations has no review comments yet, so is a slightly different logic loop.
            if i == 0 and not self.one_done:
                plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')

                # Send the coder the plan - Let it generate a first code iteration
                self.user_proxy.initiate_chat(
                    self.coder,
                    message=plan_message,
                )

                # Write the coder's code to a script_vn.py file
                self.write_latest_iteration_manual(self.coder.last_message()['content'])

                # Send the reviewer the plan and the code - Let it generate some feedback
                self.user_proxy.initiate_chat(
                    self.reviewer,
                    message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + self.read_text_file(self.working_dir + self.retrieve_latest_iteration())
                )

                # Write the reviewer's comments to a comments_vn.py file
                self.write_latest_iteration_comments(self.reviewer.last_message()['content'])

            # If not the first iteration, do regular iteration
            else:
                if self.one_done:
                    # Send coder the plan, latest code iteration, and last review
                    plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                    code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())
                    code_review_comments = self.read_text_file(self.working_dir + self.retrieve_latest_iteration_comment())

                    self.user_proxy.initiate_chat(
                        self.coder,
                        message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration + '\n\n Latest Code Review Comments \n\n' + code_review_comments
                    )

                    self.resumed_flow = False
                else:
                    # Send coder the plan, latest code iteration, and last review
                    plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                    code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())

                    self.user_proxy.initiate_chat(
                        self.coder,
                        message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration + '\n\n Latest Code Review Comments \n\n' + self.reviewer.last_message()['content']
                    )

                # Write the coder's code to a script_vn.py file
                self.write_latest_iteration_manual(self.coder.last_message()['content'])

                # Send the reviewer the plan and the code - Let it generate some feedback
                plan_message = self.read_text_file(self.working_dir + 'MasterPlan.txt')
                code_iteration = self.read_text_file(self.working_dir + self.retrieve_latest_iteration())

                self.user_proxy.initiate_chat(
                    self.reviewer,
                    message=plan_message + '\n\n\n Latest Code Iteration \n\n\n' + code_iteration
                )

                self.write_latest_iteration_comments(self.reviewer.last_message()['content'])

