from dotenv import load_dotenv
import aws_cdk as cdk
import os

from stack import EmailsFlowStack

load_dotenv()

APP_ENV = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

app = cdk.App()

async_lambda_stack = EmailsFlowStack(app, "EmailsFlowStack", env=APP_ENV)

app.synth()
