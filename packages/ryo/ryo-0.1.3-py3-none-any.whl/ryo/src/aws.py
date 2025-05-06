import boto3
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential, wait_fixed
from tenacity.retry import retry_if_result

@staticmethod
def retry_func(status):
    print("Current status:", status, flush=True)
    if status == "vfailed":
        raise Exception("Execution failed.")
    elif status == "timed_out":
        raise Exception("Execution timed out.")
    elif status == "aborted":
        raise Exception("Execution was aborted.")
    return status == "running"

class AWS:
    def __init__(self, aws_account, step_function_name, aws_region):
        self.aws_region = aws_region
        self.step_function_name = step_function_name
        self.aws_account = aws_account
        self.state_machine_arn = f'arn:aws:states:{aws_region}:{aws_account}:stateMachine:{step_function_name}'

    def get_client(self):
        try:
            print("Getting client ...")
            stepfunction_client = boto3.client(
            'stepfunctions',
            region_name=self.aws_region
            )
            return stepfunction_client
        except Exception as e:
            print("Error getting client:", e)

    def start_execution(self, client):
        try:
            print("Start execution ...")
            response = client.start_execution(
                stateMachineArn=self.state_machine_arn
            )
            print("Execution ARN:", response['executionArn'])
            return response["executionArn"]
        except Exception as e:
            print("Error starting execution:", e)
    
    @staticmethod
    def retry_func(status):
        print("Current status:", status, flush=True)
        if status == "vfailed":
            raise Exception("Execution failed.")
        elif status == "timed_out":
            raise Exception("Execution timed out.")
        elif status == "aborted":
            raise Exception("Execution was aborted.")
        return status == "running"

        
    def get_execution(self, execution_arn, client):
        print("ENTRANDO NO GET EXECUTION")
        try:
            response = client.describe_execution(
            executionArn=execution_arn
            )
            print(f"Status: {response['status'].lower()}")
            return response['status'].lower()
        except Exception as e:
            print("Error getting execution:", e)

    # @retry(
    # retry=retry_if_result(retry_func),
    # # wait=wait_exponential(multiplier=2, min=1, max=256),
    # wait=wait_fixed(10),
    # stop=stop_after_attempt(3600))
    # def check_execution_status(self, client, execution_arn):
    #     status = self.get_execution(execution_arn=execution_arn, client=client)
    #     print(f"Status get execution: {status}")
    #     return status 
    @retry(
        retry=retry_if_result(retry_func),
        wait=wait_fixed(10),
        stop=stop_after_attempt(3600))
    def check_execution_status(self, client, execution_arn):

        status = self.get_execution(execution_arn=execution_arn, client=client)
        print(f"Status get execution: {status}")
        return status 
    
    def start_step_function(self):
        """Realiza a alteracao de um arquivo dentro do repositorio."""
        print(f"\n------------- Iniciando o start da Step Function ------------")

        client = self.get_client()
        execution_arn = self.start_execution(client=client)
        final_status = self.check_execution_status(execution_arn=execution_arn, client=client)
        print("Final status:", final_status, flush=True)