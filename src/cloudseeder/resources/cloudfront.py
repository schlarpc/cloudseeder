from . import Resource

RESOURCE_TYPE_PREFIX = 'AWS.CloudFront'

class OriginAccessIdentity(Resource):
    props = {
        'CallerReference': (str, True),
        'Comment': (str, False),
    }

    @staticmethod
    def _get_return_values(response):
        physical_id = response['CloudFrontOriginAccessIdentity']['Id']
        attributes = {
             'S3CanonicalUserId': response['CloudFrontOriginAccessIdentity']['S3CanonicalUserId'],
        }
        return physical_id, attributes

    def create(self, request, session):
        cloudfront = session.client('cloudfront')
        response = cloudfront.create_cloud_front_origin_access_identity(
            CloudFrontOriginAccessIdentityConfig={
                'CallerReference': self.CallerReference,
                'Comment': getattr(self, 'Comment', ''),
            },
        )
        return self._get_return_values(response)

    def update(self, request, session):
        cloudfront = session.client('cloudfront')
        response = cloudfront.update_cloud_front_origin_access_identity(
            Id=request.physical_resource_id,
            CloudFrontOriginAccessIdentityConfig={
                'CallerReference': self.CallerReference,
                'Comment': getattr(self, 'Comment', ''),
            },
        )
        return self._get_return_values(response)

    def delete(self, request, session):
        cloudfront = session.client('cloudfront')
        cloudfront.delete_cloud_front_origin_access_identity(
            Id=request.physical_resource_id,
        )
