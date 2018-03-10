import argparse
import contextlib
import io
import json
import os.path
import site
import sys
import sysconfig
import zipfile

import six
from troposphere import Template, GetAtt, Output, Export
from troposphere.awslambda import Function
from troposphere.iam import Role

from .constants import LAMBDA_ARN_EXPORT

class FunctionLocalCode(Function):
    props = Function.props.copy()
    props['Code'] = (str, True)

def is_virtualenv():
    if hasattr(sys, 'real_prefix'):
        # virtualenv
        return True
    if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        # pyvenv
        return True
    return False

def get_site_packages():
    # this is only accurate inside a virtualenv! outside, the world is far more complicated.
    return sysconfig.get_path('purelib')

@contextlib.contextmanager
def in_memory_zip():
    with io.BytesIO() as f:
        with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.get_bytes = f.getvalue
            yield zipf

def get_files_recursive(path):
    for root, _, files in os.walk(path, followlinks=True):
        for file in files:
            yield os.path.join(root, file)

def create_environment_zip(site_packages_root):
    with in_memory_zip() as zipf:
        for file in get_files_recursive(site_packages_root):
            if file.endswith('.pyc'):
                continue
            with open(file, 'rb') as f:
                zipi = zipfile.ZipInfo(os.path.relpath(file, site_packages_root))
                zipi.create_system = 3
                zipi.external_attr = 0o755 << int(16)
                zipf.writestr(zipi, f.read(), zipfile.ZIP_DEFLATED)
        return zipf.get_bytes()

def create_template(zip_path):
    template = Template(
        Description='CloudFormation custom resource creator, part of cloudseeder',
    )
    role = template.add_resource(Role(
        'CloudSeederRole',
        ManagedPolicyArns=[
            # custom resources pretty much need to be able to do anything...
            'arn:aws:iam::aws:policy/AdministratorAccess',
        ],
        # I'd use awacs but it seems like a bit of a waste
        AssumeRolePolicyDocument={
            'Version': '2012-10-17',
            'Statement': [{
                'Effect': 'Allow',
                'Principal': {
                    'Service': ['lambda.amazonaws.com'],
                },
                'Action': ['sts:AssumeRole'],
            }],
        },
    ))
    function = template.add_resource(FunctionLocalCode(
        'CloudSeederLambda',
        Code=os.path.abspath(zip_path),
        Handler='cloudseeder.lambda_handler',
        MemorySize=256,
        Role=GetAtt(role, 'Arn'),
        Timeout=300,
        Runtime='python2.7' if six.PY2 else 'python3.6',
    ))
    template.add_output(Output(
        LAMBDA_ARN_EXPORT,
        Value=GetAtt(function, 'Arn'),
        Export=Export(LAMBDA_ARN_EXPORT),
    ))
    return json.dumps(template.to_dict(), indent=4, sort_keys=True) + '\n'

def get_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--code-output', default='cloudseeder-code.zip')
    parser.add_argument('--template-output', default='cloudseeder-template.json')
    return parser.parse_args()

def main(argv=None):
    args = get_args(argv)
    with open(args.code_output, 'wb') as f:
        f.write(create_environment_zip(get_site_packages()))
    with open(args.template_output, 'w', encoding='utf-8') as f:
        f.write(create_template(args.code_output))

if __name__ == '__main__':
    sys.exit(main())
