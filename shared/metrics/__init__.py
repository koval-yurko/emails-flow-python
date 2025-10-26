from datetime import datetime, timezone
import boto3

cloudwatch = boto3.client('cloudwatch')

def email_store_success_inc():
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'EmailStoreSuccess',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'email-store'}
                ]
            }
        ]
    )

def email_store_error_inc(errorType: str):
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'EmailStoreError',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'email-store'},
                    {'Name': 'ErrorType', 'Value': errorType },
                ]
            }
        ]
    )