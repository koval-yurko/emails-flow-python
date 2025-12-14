import os
from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    CfnOutput,
)
from constructs import Construct


class EmailsFlowApiGateway(Construct):
    """
    REST API Gateway for emails-flow Lambda functions.

    Exposes:
    - POST /read - Triggers emails-read Lambda
    - POST /analyze - Triggers emails-analyze Lambda

    Authentication: API Key (x-api-key header)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        emails_read_function: _lambda.Function,
        emails_analyze_function: _lambda.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create REST API
        self.api = apigw.RestApi(
            self,
            "Api",
            rest_api_name="emails-flow-api",
            description="API Gateway for emails-flow Lambda functions",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=10,  # Requests per second
                throttling_burst_limit=20,
            ),
        )

        # Create API Key from environment variable
        api_key_value = os.getenv("API_GATEWAY_KEY")
        if not api_key_value:
            raise ValueError("API_GATEWAY_KEY environment variable is required")

        if len(api_key_value) < 20:
            raise ValueError("API_GATEWAY_KEY must be at least 20 characters")

        self.api_key = apigw.ApiKey(
            self,
            "ApiKey",
            api_key_name="emails-flow-api-key",
            value=api_key_value,
        )

        # Create Usage Plan
        self.usage_plan = apigw.UsagePlan(
            self,
            "UsagePlan",
            name="emails-flow-usage-plan",
            description="Usage plan for emails-flow API",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,
                burst_limit=20,
            ),
            quota=apigw.QuotaSettings(
                limit=1000,
                period=apigw.Period.DAY,
            ),
        )

        # Associate API Key with Usage Plan
        self.usage_plan.add_api_key(self.api_key)
        self.usage_plan.add_api_stage(
            stage=self.api.deployment_stage,
        )

        # Create Lambda integrations with proxy integration
        emails_read_integration = apigw.LambdaIntegration(
            emails_read_function,
            proxy=True,
            allow_test_invoke=True,
        )

        emails_analyze_integration = apigw.LambdaIntegration(
            emails_analyze_function,
            proxy=True,
            allow_test_invoke=True,
        )

        # Create /read endpoint
        read_resource = self.api.root.add_resource("read")
        read_resource.add_method(
            "POST",
            emails_read_integration,
            api_key_required=True,
        )

        # Create /analyze endpoint
        analyze_resource = self.api.root.add_resource("analyze")
        analyze_resource.add_method(
            "POST",
            emails_analyze_integration,
            api_key_required=True,
        )
