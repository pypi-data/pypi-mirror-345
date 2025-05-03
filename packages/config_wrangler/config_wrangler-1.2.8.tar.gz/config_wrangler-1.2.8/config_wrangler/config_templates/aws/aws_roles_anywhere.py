# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# AWS Version 4 signing example

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a POST request and passes request parameters
# in the body (payload) of the request. Auth information is passed in
# an Authorization header.
import sys, os, base64, datetime, hashlib
import requests # pip install requests
from cryptography import x509 # pip install cryptography
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def main():
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/create-signed-request.html#sig-v4-examples-post
    # https://nerdydrunk.info/aws:roles_anywhere

    private_key_file = '' # PEM format
    pass_phrase = '' # If encrypted
    public_certificate_file = '' # PEM format
    region = '' # AWS Region
    duration_seconds = '' # From 900 to 3600
    profile_arn = '' # Roles Anywhere Profile ARN
    role_arn = '' # IAM Role ARN
    session_name = ''
    trust_anchor_arn = '' # Roles Anywhere Trust Anchor ARN

    # ************* REQUEST VALUES *************
    method = 'POST'
    service = 'rolesanywhere'
    host = 'rolesanywhere.{}.amazonaws.com'.format(region)
    endpoint = 'https://rolesanywhere.{}.amazonaws.com'.format(region)
    # POST requests use a content type header.
    content_type = 'application/json'


    # Load private key
    try:
        with open(private_key_file, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(),password=None)
    except:
        print('encrypted')
        try:
            with open(private_key_file, 'rb') as f:
                private_key = serialization.load_pem_private_key(f.read(),password=str.encode(pass_phrase))
        except:
            print('wrong passphrase')
            sys.exit()

    # Load public certificate
    with open(public_certificate_file, 'r') as f:
        cert = x509.load_pem_x509_certificate(f.read().encode())
    amz_x509 = str(base64.b64encode(cert.public_bytes(encoding=serialization.Encoding.DER)),'utf-8')

    # Public certificate serial number in decimal
    serial_number_dec = cert.serial_number

    # Request parameters for CreateSession--passed in a JSON block.
    request_parameters =  '{'
    request_parameters +=  '"durationSeconds": {},'.format(duration_seconds)
    request_parameters +=  '"profileArn": "{}",'.format(profile_arn)
    request_parameters +=  '"roleArn": "{}",'.format(role_arn)
    request_parameters +=  '"sessionName": "{}",'.format(session_name)
    request_parameters +=  '"trustAnchorArn": "{}"'.format(trust_anchor_arn)
    request_parameters +=  '}'

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

    # Step 1 is to define the verb (GET, POST, etc.)--already done.

    # Step 2: Create canonical URI--the part of the URI from domain to query
    # string (use '/' if no path)
    canonical_uri = '/sessions'

    ## Step 3: Create the canonical query string. In this example, request
    # parameters are passed in the body of the request and the query string
    # is blank.
    canonical_querystring = ''

    # Step 4: Create the canonical headers. Header names must be trimmed
    # and lowercase, and sorted in code point order from low to high.
    # Note that there is a trailing \n.
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amz_date + '\n' + 'x-amz-x509:' + amz_x509 + '\n'

    # Step 5: Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    # Note: The request can include any headers; canonical_headers and
    # signed_headers include those that you want to be included in the
    # hash of the request. "Host" and "x-amz-date" are always required.
    # For Roles Anywhere, content-type and x-amz-x509 are also required.
    signed_headers = 'content-type;host;x-amz-date;x-amz-x509'

    # Step 6: Create payload hash. In this example, the payload (body of
    # the request) contains the request parameters.
    payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

    # Step 7: Combine elements to create canonical request
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    # Match the algorithm to the hashing algorithm you use, SHA-256
    algorithm = 'AWS4-X509-RSA-SHA256'
    credential_scope = date_stamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    # Sign the string_to_sign using the private_key and hex encode
    signature = private_key.sign(
        data=string_to_sign.encode('utf-8'),
        padding=padding.PKCS1v15(),
        algorithm=hashes.SHA256()
    )
    signature_hex = signature.hex()

    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    # Put the signature information in a header named Authorization.
    authorization_header = algorithm + ' ' + 'Credential=' + str(serial_number_dec) + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature_hex

    # For Roles Anywhere, the request  MUST include "host", "x-amz-date",
    # "x-amz-x509", "content-type", and "Authorization". Except for the authorization
    # header, the headers must be included in the canonical_headers and signed_headers values, as
    # noted earlier. Order here is not significant.
    # # Python note: The 'host' header is added automatically by the Python 'requests' library.
    headers = {'Content-Type':content_type,
               'X-Amz-Date':amz_date,
               'X-Amz-X509':amz_x509,
               'Authorization':authorization_header}

    # ************* SEND THE REQUEST *************
    print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
    print('Request URL = ' + endpoint)

    r = requests.post(endpoint + canonical_uri, data=request_parameters, headers=headers)

    print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
    print('Response code: %d\n' % r.status_code)
    print(r.text)


if __name__ == '__main__':
    main()
