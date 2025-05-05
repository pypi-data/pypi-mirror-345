import requests
import boto3
from botocore.auth import SigV4Auth, S3SigV4Auth
from botocore.awsrequest import AWSRequest

session = boto3.Session()
credentials = session.get_credentials()
creds = credentials.get_frozen_credentials()

def signed_request(method, url, data=None, params=None, headers=None):
    request = AWSRequest(method=method, url=url, data=data, params=params, headers=headers)
    # "service_name" is generally "execute-api" for signing API Gateway requests
    S3SigV4Auth(creds, "s3", "eu-west-1").add_auth(request)
    # request = request.prepare()
    return requests.request(method=method, url=url, headers=dict(request.headers), data=data)


# # Set up the CloudFront signed URL
cloudfront_url = 'https://data.crypto-lake.com/market-data/cryptofeed/book/exchange=BINANCE_FUTURES/symbol=BTC-USDT-PERP/dt=2023-08-25/1.snappy.parquet'
# cloudfront_url = 'http://de1dx49q6xt2q.cloudfront.net/book/exchange=BINANCE_FUTURES/symbol=BTC-USDT-PERP/dt=2023-09-13/1.snappy.parquet'

# response = requests.get(cloudfront_url)
# response = signed_request('GET', cloudfront_url)

from aws_requests_auth.aws_auth import AWSRequestsAuth
auth = AWSRequestsAuth(
    aws_access_key=credentials.access_key,
    aws_secret_access_key=credentials.secret_key,
    aws_host='qnt.data.s3.amazonaws.com',
    aws_region='eu-west-1',
    aws_service='s3'
)
response = requests.get(cloudfront_url, auth = auth, headers = {'Referer': 'test/jsk', 'User-Agent': 'lakeapi/0.10.0rc1'})

print(response)
print(response.request.headers)
if response.content[:4] != b'PAR1':
    print(response.content) #[:1000])

# s3 = boto3.resource('s3')
# cf = boto3.client('cloudfront')

