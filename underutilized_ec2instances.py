import json
import boto3
from datetime import datetime, timedelta, timezone
import time
def lambda_handler(event, context):
# Event coming from SQS
     print(event)
     for records in event['Records']:
          body = records['body']
          json_obj = json.loads(body)
          if json_obj['detail']['check-item-detail']['Number of Days Low Utilization'] == '14 days' :
               instance_id = json_obj['detail']['check-item-detail']['Instance ID']
               region_val = json_obj['detail']['check-item-detail']['Region/AZ']
               length = len(region_val)
               region = region_val[:(length-1)]
               print("region", region)
#Fetch instance details from Event 
               session = boto3.Session(region_name=region)
               ec2 = session.resource(service_name='ec2')
               instance_detail = ec2.Instance(instance_id)
               print( instance_id , instance_detail.launch_time,  instance_detail.tags)
               current= datetime.now(timezone.utc)
               if (current - instance_detail.launch_time) > timedelta(days=60):
#if Tag with Retention is Yes, don't terminate 
                    tag = {'Key': 'Retention', 'Value': 'Yes'}
                    if ( tag in instance_detail.tags):
                         print('Do not terminate')
                         break
                    else:
#terminate instance
                         print('image creation complete and can terminate')
                         ec2.instances.filter(InstanceIds= [ instance_id ]).terminate()
                         print('Instance Termination in progress ...')
                    print('Instance launch_time is less than 60 days, so we can not terminate')
