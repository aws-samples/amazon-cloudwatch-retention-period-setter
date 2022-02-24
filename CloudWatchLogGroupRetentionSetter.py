# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# NOTES
# This function would automatically set a desirable retention period for the existing/newly created CloudWatch log groups across different AWS regions
 
import boto3
from botocore.config import Config
import logging
import os
 
 
# Appropriate logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
 
 
# Specify the regions to scan its log groups and set retention period for
# Valid values for REGIONS_TO_SCAN variable? Possible values are the regions’ codes, i.e., us-east-1, us-east-2, us-west-1
regions = [item.strip() for item in os.environ['REGIONS_TO_SCAN'].split(",") if item] 
 
# Specify the retention period in days
# valid values? Possible values are: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, and 3653.
RETENTION_PERIOD_IN_DAYS = int(os.environ.get('RETENTION_DAYS', 30))
VALID_RETENTION_PERIOD_VALUES = [1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653]
 
# Making sure we configure our boto3 client with a different Retry Configuration
custom_config = Config(
   retries = {
      'max_attempts': 10,
      'mode': 'adaptive'
   }
)
 
def lambda_handler(event, context):
    
    # log your environment variables
    LOGGER.info(f"Regions to be scanned = {regions}")
    LOGGER.info(f"Retention period to be set = {RETENTION_PERIOD_IN_DAYS}")
    
    # test retention period for a valid value
    if RETENTION_PERIOD_IN_DAYS not in VALID_RETENTION_PERIOD_VALUES:
        return {'statusCode': 200, 'body': '`RETENTION_PERIOD_IN_DAYS` is set to `' + str(RETENTION_PERIOD_IN_DAYS) + '`. Valid values are  1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, and 3653.'}
    
    # test the regions 
    if not regions:
        return {'statusCode': 200, 'body': 'No regions found in `REGIONS_TO_SCAN` variable. Have you configured it?'}
    
    
    # Iterate through each region, setting boto3 client accordingly
    for aws_region in regions:
        client = boto3.client('logs',region_name=aws_region, config=custom_config)
        response = client.describe_log_groups()
        nextToken=response.get('nextToken',None)
        retention = response['logGroups']
 
        while (nextToken is not None):
            response = client.describe_log_groups(nextToken=nextToken)
            nextToken = response.get('nextToken', None)
            retention = retention.append(response['logGroups'])
 
        for group in retention:
            if 'retentionInDays' in group.keys():
                LOGGER.info(f"Retention is already set for {group['logGroupName']} LogGroup, {group['retentionInDays']} in {aws_region}")
            else:
                LOGGER.info(f"Retention is not set for {group['logGroupName']} LogGroup,in {aws_region}")
                
                setretention = client.put_retention_policy(
                    logGroupName=group['logGroupName'],
                    retentionInDays= RETENTION_PERIOD_IN_DAYS
                    )
                LOGGER.info(f"PutRetention result {setretention}")
    
    return {'statusCode': 200, 'body': 'Process completed.'}
