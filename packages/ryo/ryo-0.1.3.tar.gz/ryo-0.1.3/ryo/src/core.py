from ryo.src.github import GitHubRepo
from pathlib import Path
from ryo.src.aws import AWS


def commit_file(step: dict, repo: GitHubRepo):
    """
    Commit a file with a message.
    
    Args:
        step (dict): The step configuration containing file path and commit message.
    """
    file_path = step.get("file_path", "README.md") 
    commit_msg = step.get("commit_msg", "Update README.md") 
    auto_commit = step.get("auto_commit", "false")
    branch = step.get("branch", "")
    
    repo.commit(commit_file=file_path, commit_message=commit_msg, auto_commit=auto_commit, branch=branch)
 

def approve_pull_request(step: dict, repo: GitHubRepo):
    """
    Approve a pull request.
    
    Args:
        step (dict): The step configuration containing target branch.
    """
    target_branch = step.get("target_branch", "develop")
    source_branch = step.get("source_branch", "")
    repo.approve_pull_request(target_branch=target_branch, source_branch=source_branch)   
    

def workflow_monitor(step: dict, repo: GitHubRepo):
    """
    Monitor a workflow.
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    workflow_name = step.get("workflow_name")
    show_workflow = step.get("show_workflow", "false").lower()
    
    repo.workflow_monitor(workflow_name=workflow_name, show_workflow=show_workflow)

def git_clone(step: dict, repo: GitHubRepo):
    """
    Git Clone
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    org = step.get("org").lower()
    branch = step.get("branch")
    
    repo.git_clone(org=org, branch=branch)

def replace_file(step: dict, repo: GitHubRepo):
    """
    Realiza o replace de um arquivo
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    source_path = Path(step.get("source_path"))
    target_path = Path(step.get("target_path"))
    
    repo.replace_file(source_path=source_path, target_path=target_path)

def replace_dir(step: dict, repo: GitHubRepo):
    """
    Realiza o replace de uma pasta
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    source_path = Path(step.get("source_path"))
    target_path = Path(step.get("target_path", ""))
    
    repo.replace_dir(source_path=source_path, target_path=target_path)

def destroy(step: dict, repo: GitHubRepo):
    """
    Realiza as alterações para que a esteira seja executada no modo de destroy
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    file_path = Path(step.get("file_path"))
    value = step.get("value")
    
    repo.destroy(file_path=file_path, value=value)

def start_step_function(step: dict):
    """
    Realiza o start da execução da step function
    
    Args:
        step (dict): The step configuration containing workflow name.
    """
    step_function_name = step.get("name")
    aws_account = step.get("account")
    aws_region = step.get("region", 'sa-east-1')
    aws = AWS(aws_account=aws_account, step_function_name=step_function_name, aws_region=aws_region)

    aws.start_step_function()


