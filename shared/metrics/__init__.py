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

def email_analyze_success_inc():
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'EmailAnalyzeSuccess',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'email-analyze'}
                ]
            }
        ]
    )

def email_analyze_error_inc(errorType: str):
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'EmailAnalyzeError',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'email-analyze'},
                    {'Name': 'ErrorType', 'Value': errorType },
                ]
            }
        ]
    )

def post_store_success_inc():
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'PostStoreSuccess',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'post-store'}
                ]
            }
        ]
    )

def post_store_error_inc(errorType: str):
    cloudwatch.put_metric_data(
        Namespace='EmailsFlow',
        MetricData=[
            {
                'MetricName': 'PostStoreError',
                'Value': 1,
                'Unit': 'Count',
                'Timestamp': datetime.now(timezone.utc),
                'Dimensions': [
                    {'Name': 'Lambda', 'Value': 'post-store'},
                    {'Name': 'ErrorType', 'Value': errorType },
                ]
            }
        ]
    )