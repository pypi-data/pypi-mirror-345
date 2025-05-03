from datetime import datetime

from pydantic import BaseModel, AnyHttpUrl


# noinspection PyPep8Naming
class _AWS_Identity_Center_Client_Auth(BaseModel):
    """
    Stores the results of the RegisterClient API call.
    This model is to aid possible persistence of this data.
    https://docs.aws.amazon.com/singlesignon/latest/OIDCAPIReference/API_RegisterClient.html
    """

    authorizationEndpoint: AnyHttpUrl
    """
    The endpoint where the client can request authorization.
    """

    clientId: str
    """
    The unique identifier string for each client. This client uses this identifier to get authenticated by the service in subsequent calls.
    """

    clientIdIssuedAt: int
    """
    Indicates the time at which the clientId and clientSecret were issued.
    """

    clientSecret: str
    """
    A secret string generated for the client. The client will use this string to get authenticated by the service in subsequent calls.
    """

    clientSecretExpiresAt: int
    """
    Indicates the time at which the clientId and clientSecret will become invalid.
    """

    tokenEndpoint: AnyHttpUrl
    """
    The endpoint where the client can get an access token.
    """

    @property
    def clientIdIssuedAtDt(self):
        return datetime.fromtimestamp(self.clientSecretExpiresAt)

    @property
    def clientSecretExpiresAtDt(self):
        return datetime.fromtimestamp(self.clientSecretExpiresAt)
