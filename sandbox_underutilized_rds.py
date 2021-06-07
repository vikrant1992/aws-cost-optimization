import json
import boto3
from datetime import datetime, timedelta, timezone
def lambda_handler(event, context):
#Event coming from SQS
    print(event)
    tag_value = {'Key':'Retention','Value':'Yes'}
    for records in event['Records']:
        body = records['body']
        json_obj = json.loads(body)
        if json_obj['detail']['check-item-detail']['Days Since Last Connection'] == '14+' :
            rds_instance_name = json_obj['detail']['check-item-detail']['DB Instance Name']
            region = json_obj['detail']['check-item-detail']['Region']
            arn = json_obj['detail']['resource_id']
            print('region', region)
            print('rds instance name',  rds_instance_name)

#if Tag with Retention is Yes, don't terminate
            rds_session = boto3.Session(region_name=region)
            rds = rds_session.client('rds')
            LT = rds.describe_db_instances(DBInstanceIdentifier= rds_instance_name  )
            launch_time = LT ['DBInstances'][0]['InstanceCreateTime']
            current= datetime.now(timezone.utc)
            if (current - launch_time) > timedelta(days=60):
                tag = rds.list_tags_for_resource( ResourceName= arn )
                if tag_value in  tag['TagList']:
                    print('Do not terminate')
                    break
                else:
                    now = datetime.now()
                    today= now.strftime("%Y-%m-%d-%H-%M-%S")
                    rds_snapshot_name = rds_instance_name + today
                    print(rds_snapshot_name)
                    print('After taking final snapshot, This script will go ahead and terminate RDS instance. ')
                    rds.delete_db_instance(
                        DBInstanceIdentifier=rds_instance_name,
                        SkipFinalSnapshot= False,
                        FinalDBSnapshotIdentifier= rds_instance_name,
                        DeleteAutomatedBackups=True
                    )