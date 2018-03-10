CloudSeeder
===========

CloudSeeder is an extension to the wonderful `troposphere` library that allows
for the easy creation of robust AWS CloudFormation custom resources.
These custom resources can be used to extend the capabilities of AWS CloudFormation
to include new services, configuration sources, or any bespoke functionality.

At the current time, this library is in an exploratory state and probably doesn't
work completely if at all. This notice will be removed once the framework is
stabilized and plugin support is added.

Usage
=====

TODO

Installing
==========

These steps use the AWS CLI to upload and deploy the stack artifacts,
and assume a POSIX shell environment. `$DEPLOYMENT_BUCKET` should
be set beforehand to a bucket you own in the account. You can add
flags like `--profile` and `--region` to the AWS CLI commands to customize
the account and region the stack will be deployed to.

    python3 -m virtualenv venv
    . venv/bin/activate
    pip install cloudseeder
    python3 -m cloudseeder.deploy
    python3 -m awscli cloudformation package \
        --template-file cloudseeder-template.json \
        --s3-bucket $DEPLOYMENT_BUCKET \
        --output-template-file cloudseeder-template-packaged.yaml
    python3 -m awscli cloudformation deploy \
        --capabilities CAPABILITY_IAM \
        --template-file cloudseeder-template-packaged.yaml \
        --stack-name CloudSeeder
    deactivate

Note: CloudSeeder must be installed into a virtualenv (or pyvenv) in order to
create its deployment artifacts. Attempting to run `cloudseeder.deploy`
outside of a virtualenv will not function.

Plugins
=======

TODO

This will use setuptools entry points or some similar mechanism to allow
the code bundle to include resource classes not defined within this package.

Testing
=======

Unit tests can be run via `python setup.py test`.
They currently pass on both Python 2.7 and Python 3.5.

Integration tests are a TODO.
