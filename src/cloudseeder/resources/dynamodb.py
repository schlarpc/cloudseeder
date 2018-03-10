from . import Resource, Property

RESOURCE_TYPE_PREFIX = 'AWS.DynamoDB'

class GlobalSecondaryIndex(Property):
    props = {
        'Name': (str, True),
    }

class Table(Resource):
    """
    The `AWS::DynamoDB::Table` resource creates a DynamoDB table. For more information, see
    [CreateTable](http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_CreateTable.html)
    in the *Amazon DynamoDB API Reference*.

    You should be aware of the following behaviors when working with DynamoDB tables:

    * AWS CloudFormation typically creates DynamoDB tables in parallel.
      However, if your template includes multiple DynamoDB tables with indexes,
      you must declare dependencies so that the tables are created sequentially.
      Amazon DynamoDB limits the number of tables with secondary indexes that are
      in the creating state. If you create multiple tables with indexes at the same
      time, DynamoDB returns an error and the stack operation fails.
      For an example, see
      [DynamoDB Table with a DependsOn Attribute](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html#cfn-dynamodb-table-examples-dependson).

    * Updates to `AWS::DynamoDB::Table` resources that are associated with
      `AWS::ApplicationAutoScaling::ScalableTarget` resources will always result in an
      update failure and then an update rollback failure. The following `ScalableDimension`
      attributes cause this problem when associated with the table:
        - dynamodb:table:ReadCapacityUnits
        - dynamodb:table:WriteCapacityUnits
        - dynamodb:index:ReadCapacityUnits
        - dynamodb:index:WriteCapacityUnits

        As a workaround, please deregister scalable targets before performing updates
        to `AWS::DynamoDB::Table` resources.
    """
    props = {
        'GlobalSecondaryIndexes': ([GlobalSecondaryIndex], True),
        'TableName': (str, False),
    }

    def create(self, request, session):
        pass


