from boto3.session import Session

from api_deploy.schema import Schema


class ApiGatewayClient(object):
    def __init__(self, access_key_id=None, secret_access_key=None,
                 region=None, profile=None, session_token=None, assume_account=None, assume_role=None):
        if assume_account and assume_role:
            access_key_id, secret_access_key, session_token = self.assume_role(access_key_id, secret_access_key, region,
                                                                               profile, session_token, assume_account,
                                                                               assume_role)
            profile = None

        session = Session(aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          aws_session_token=session_token,
                          region_name=region,
                          profile_name=profile)
        self.boto = session.client('apigateway')

    @staticmethod
    def assume_role(access_key_id=None, secret_access_key=None, region=None, profile=None, session_token=None,
                    assume_account=None, assume_role=None):
        role_arn = 'arn:aws:iam::%s:role/%s' % (assume_account, assume_role)
        sts_session = Session(aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key,
                              aws_session_token=session_token,
                              region_name=region,
                              profile_name=profile)
        sts = sts_session.client('sts')
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName='apiDeploy',
        )
        access_key_id = response['Credentials']['AccessKeyId']
        secret_access_key = response['Credentials']['SecretAccessKey']
        session_token = response['Credentials']['SessionToken']
        return access_key_id, secret_access_key, session_token

    def import_openapi(self, schema: Schema, api_id: str):
        self.boto.put_rest_api(
            restApiId=api_id,
            failOnWarnings=False,
            mode='overwrite',
            body=schema.dump().encode()
        )

    def deploy_to_stage(self, api_id: str, stage_name: str):
        self.boto.create_deployment(
            restApiId=api_id,
            stageName=stage_name
        )
