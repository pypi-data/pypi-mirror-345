from datetime import datetime

from pydantic import BaseModel, AnyHttpUrl, PrivateAttr

from config_wrangler.config_templates.aws._aws_identity_center_client_auth import _AWS_Identity_Center_Client_Auth
from config_wrangler.config_templates.aws.aws_session import AWS_Session


# noinspection PyPep8Naming
class AWS_Identity_Center_Session(AWS_Session):
    ic_client_name: str
    ic_client_type: str = 'public'
    """
    The type of client. The service supports only public as a client type. 
    Anything other than public will be rejected by the service.
    """

    _ic_client_auth: _AWS_Identity_Center_Client_Auth = PrivateAttr(default=None)
    """
    In memory persisted results of the RegisterClient API call
    https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_RegisterClient.html
    """



# See https://docs.aws.amazon.com/singlesignon/latest/userguide/howtogetcredentials.html

def get_role_credentials(sso, role_name, account_id):
    role_cred_response = sso.get_role_credentials(
        roleName=role_name,
        accountId=account_id,
        accessToken=access_token,
    )
    if role_cred_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise ValueError(f"get_role_credentials response = {role_cred_response['ResponseMetadata']['HTTPStatusCode']}")
    role_creds = role_cred_response['roleCredentials']
    expires_at = datetime.fromtimestamp(role_creds['expiration']/1000)
    print(f"Creds expire at = {expires_at}")


def main():
    from time import sleep
    import webbrowser
    from boto3.session import Session

    ################
    # Config items
    # 1) SSO general
    sso_client_name = 'test_ic_etl'
    sso_start_url = 'https://baosystems.awsapps.com/start'
    region = 'us-east-1'

    # 2) Assume role details
    account_id = '973612564635'
    role_name = 'AdministratorAccess'

    # Static
    sso_client_type = 'public'

    sso_session = Session(region_name=region)
    sso_oidc = sso_session.client('sso-oidc')
    client_creds = sso_oidc.register_client(
        clientName=sso_client_name,
        clientType=sso_client_type,
    )
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds['clientId'],
        clientSecret=client_creds['clientSecret'],
        startUrl=sso_start_url,
    )
    completion_url = device_authorization['verificationUriComplete']
    device_code = device_authorization['deviceCode']
    expires_in = device_authorization['expiresIn']
    interval = device_authorization['interval']
    webbrowser.open(completion_url, autoraise=True)
    token = None

    # Try getting a token until complete or expired
    for n in range(1, expires_in // interval + 1):
        try:
            token = sso_oidc.create_token(
                grantType='urn:ietf:params:oauth:grant-type:device_code',
                deviceCode=device_code,
                clientId=client_creds['clientId'],
                clientSecret=client_creds['clientSecret'],
            )
            # Success, break from the loop
            break
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass
        sleep(interval)

    if token is None:
        raise RuntimeError("Unable to complete authentication in time")

    access_token = token['accessToken']
    sso = sso_session.client('sso')
    account_roles = sso.list_account_roles(
        accessToken=access_token,
        accountId=account_id,
    )
    # {
    #     'nextToken': 'string',
    #     'roleList': [
    #         {
    #             'roleName': 'string',
    #             'accountId': 'string'
    #         },
    #     ]
    # }
    roles = account_roles['roleList']

    #  Find the correct role by name / id
    role = None
    for candidate_role in roles:
        print(f"candidate_role = {candidate_role}")
        if candidate_role['roleName'] == role_name:
            role = candidate_role
    if role is None:
        raise ValueError(f"Session {sso_session} does not have access to role {role_name}")

    role_cred_response = sso.get_role_credentials(
        roleName=role_name,
        accountId=account_id,
        accessToken=access_token,
    )
    if role_cred_response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise ValueError(f"get_role_credentials response = {role_cred_response['ResponseMetadata']['HTTPStatusCode']}")
    role_creds = role_cred_response['roleCredentials']
    expires_at = datetime.fromtimestamp(role_creds['expiration']/1000)
    print(f"Creds expire at = {expires_at}")

    session = Session(
        region_name=region,
        aws_access_key_id=role_creds['accessKeyId'],
        aws_secret_access_key=role_creds['secretAccessKey'],
        aws_session_token=role_creds['sessionToken'],
    )

    print(session)

# TOTP Example
# https://kevinhakanson.com/2017-10-21-creating-and-using-an-aws-virtual-mfa-device-with-the-aws-sdk-for-python/
def login_totp():
    sts_client = session.client('sts')

    totp = pyotp.TOTP(string_seed)
    token_code = totp.now()

    response = sts_client.assume_role(
        RoleArn='arn:aws:iam::123456789012:role/kjh-DuperRole',
        RoleSessionName='my-python-session',
        SerialNumber='arn:aws:iam::123456789012:mfa/service-user/kjh-SuperDuperUser',
        TokenCode=token_code
    )

    session = boto3.session.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )


if __name__ == '__main__':
    main()
