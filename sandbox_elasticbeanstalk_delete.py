import json
import boto3
from datetime import datetime , timezone ,timedelta
#from datetime import timedelta
def lambda_handler(event, context):
    all_regions = []
#find out region
    regions = boto3.client('ec2').describe_regions()
    for reg in regions['Regions']:
        all_regions.append(reg['RegionName'])
    for current_region in all_regions:
        session = boto3.Session(region_name = current_region)
        eb = session.client('elasticbeanstalk')
        app = []
#Describe applications
        apps = eb.describe_applications()
        for applications in apps['Applications']:
            app.append(applications['ApplicationName'])
        print(app)
#Describe environments
        for app_name in app:
            env = eb.describe_environments( ApplicationName = app_name)
            for resource in env['Environments']:
                print( resource['EnvironmentName'])
                current= datetime.now(timezone.utc)  # timzone.ut should use: error: Can't subtract offset-naive and offset-aware datetimes
                eb_lastupdate =  resource['DateUpdated']
#Terminate environments
                if (current - eb_lastupdate) > timedelta(days=60):
                    eb.terminate_environment(
                        EnvironmentId= resource['EnvironmentId'] ,
                        EnvironmentName= resource['EnvironmentName'],
                        TerminateResources=True,
                        ForceTerminate=True
)