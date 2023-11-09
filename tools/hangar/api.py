import json
import os
import time
from typing import List

import dotenv
import requests
from pydantic import BaseModel


dotenv.load_dotenv()

AwsAccountId = os.getenv("AWS_ACCOUNT_ID")
TenantId = os.getenv("HANGAR_TENANT_ID")
HangarURL = os.getenv("HANGAR_URL")
GithubPk = os.getenv("GITHUB_PK")
SSHKey = os.getenv("HANGAR_SSH_KEY")

class BuildDefinition(BaseModel):
    projectName: str
    awsAccountId: str = AwsAccountId
    userId: int = 0
    githubRepoUrl: str

class ActionRequest(BaseModel):
    namespace: str
    resource_type: str
    action_type: str
    action_data: dict

class HangarProject(BaseModel):
    projectName: str
    ssh_key: str
    userId: int = 0
    githubToken: str = GithubPk

    def makeBuildPayload(self, namespace:str, githubRepoUrl: str):
        definition = BuildDefinition(
            projectName=self.projectName,
            awsAccountId=AwsAccountId,
            userId=self.userId,
            githubRepoUrl=githubRepoUrl
        )

        return {
            "namespace": namespace,
            "resource_type": "Project",
            "action_type": "build",
            "action_data": {
                "projectName": definition.projectName,
                "awsAccountId": definition.awsAccountId,
                "userId": definition.userId,
                "githubRepoUrl": definition.githubRepoUrl
            }
        }

class Workspace(BaseModel):
    workspaceName: str
    projectDefinitions: List[HangarProject] = []

    def addProjects(self, projects: (List[HangarProject] | HangarProject)):
        if isinstance(projects, HangarProject):
            self.projectDefinitions.append(projects)
        elif isinstance(projects, List) and len(projects) > 0 and isinstance(projects[0], HangarProject):
            self.projectDefinitions.extend(projects)


class HangarClient:
    headers = {"Content-Type": "application/json"}

    def __init__(self, namespace: str):
        self.roleArn = "arn:aws:iam::" + AwsAccountId + ":role/name"
        self.namespace = "_".join([TenantId, namespace])
        self.workspaces = []

    def form_payload(self, workspaces: List[Workspace]):
        resources = []
        for workspace in workspaces:
            resource = {
                "name": workspace.workspaceName,
                "type": "Workspace",
                "properties": {
                    "workspaceName": workspace.workspaceName,
                    "projectDefinitions": [project.model_dump() for project in workspace.projectDefinitions]
                }
            }
            resources.append(resource)

        payload = {
            "namespace": self.namespace,
            "buffers": {
                "terraform": {
                    "name": "terraform",
                    "credential": {
                        "roleArn": self.roleArn
                    },
                    "resources": resources
                },
                "kubernetes": {
                    "name": "kubernetes"
                }
            },
            "loggingStrategy": "Hangar"
        }
        return payload

    def provision(self, workspaces: List[Workspace]):
        payload = self.form_payload(workspaces)

        response = requests.post(f"{HangarURL}/apply", json=payload, headers=self.headers)
        return response.json()

    def deploy(self, project: HangarProject, githubRepoUrl: str):
        # Assuming `buildDefinition` is a dictionary with the build configuration
        response = requests.post(f"{HangarURL}/execute", json=project.makeBuildPayload(namespace=self.namespace, githubRepoUrl=githubRepoUrl), headers=self.headers)
        return response.json()

    def getStatus(self, deployerResponse: dict):

        sessionId = deployerResponse["apply_job_id"]
        response = requests.get(f"{HangarURL}/status/{sessionId}", json={}, headers=self.headers)


        while not response.ok:
            time.sleep(5)
            response = requests.get(f"{HangarURL}/status/{sessionId}", json={}, headers=self.headers)

        return response.json()

if __name__ == "__main__":
    client = HangarClient(namespace="my_namespace")
    w = Workspace(workspaceName="test")
    p = HangarProject(
        projectName="newhope",
        ssh_key=SSHKey
    )
    w.addProjects(p)
    r1 = client.provision([w])
    print(r1)
    r2 = client.getStatus(r1)

    while not (
            len(r2["status"]["output"]["output"]) > 0 and
            "lb_dns" in r2["status"]["output"]["output"] and
            "value" in r2["status"]["output"]["output"]["lb_dns"]
    ):
        r2 = client.getStatus(r1)
        time.sleep(5)
        print(r2)

    url = r2["status"]["output"]["output"]["lb_dns"]["value"]

    r3 = client.deploy(project=p, githubRepoUrl="https://github.com/entropy-infrastructure/test-build")

    print(url)
