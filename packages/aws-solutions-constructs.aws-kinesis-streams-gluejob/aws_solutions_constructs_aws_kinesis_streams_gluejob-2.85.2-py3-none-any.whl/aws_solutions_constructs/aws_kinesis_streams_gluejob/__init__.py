r'''
# aws-kinesisstreams-gluejob module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**: | <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span> |
| :--------------------------- | :------------------------------------------------------------------------------------------------ |

<div style="height:8px"></div>

| **Language**                                                                                   | **Package**                                                    |
| :--------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| ![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python             | `aws_solutions_constructs.aws_kinesis_streams_gluejob`         |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript | `@aws-solutions-constructs/aws-kinesisstreams-gluejob`         |
| ![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java                   | `software.amazon.awsconstructs.services.kinesisstreamsgluejob` |

## Overview

This AWS Solutions Construct deploys a Kinesis Stream and configures a AWS Glue Job to perform custom ETL transformation with the appropriate resources/properties for interaction and security. It also creates an S3 bucket where the python script for the AWS Glue Job can be uploaded.

Here is a minimal deployable pattern definition:

Typescript

```python
import * as glue from "@aws-cdk/aws-glue";
import * as s3assets from "@aws-cdk/aws-s3-assets";
import { KinesisstreamsToGluejob } from "@aws-solutions-constructs/aws-kinesisstreams-gluejob";

const fieldSchema: glue.CfnTable.ColumnProperty[] = [
  {
    name: "id",
    type: "int",
    comment: "Identifier for the record",
  },
  {
    name: "name",
    type: "string",
    comment: "Name for the record",
  },
  {
    name: "address",
    type: "string",
    comment: "Address for the record",
  },
  {
    name: "value",
    type: "int",
    comment: "Value for the record",
  },
];

const customEtlJob = new KinesisstreamsToGluejob(this, "CustomETL", {
  glueJobProps: {
    command: {
      name: "gluestreaming",
      pythonVersion: "3",
    },
  },
  fieldSchema: fieldSchema,
  etlCodeAsset: new s3assets.Asset(this, "ScriptLocation", {
    path: `${__dirname}/../etl/transform.py`,
  }),
});
```

## Pattern Construct Props

| **Name**            | **Type**                                                                                                                      | **Description**                                                                                                  |
| :------------------ | :---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| existingStreamObj?  | [`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kinesis.Stream.html)                          | Existing instance of Kinesis Stream, providing both this and `kinesisStreamProps` will cause an error.           |
| kinesisStreamProps? | [`kinesis.StreamProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kinesis.StreamProps.html)                | Optional user-provided props to override the default props for the Kinesis stream.                               |
| glueJobProps?       | [`cfnJob.CfnJobProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnJobProps.html)                    | User provided props to override the default props for the AWS Glue Job.                                          |
| existingGlueJob?    | [`cfnJob.CfnJob`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnJob.html)                              | Existing instance of AWS Glue Job, providing both this and `glueJobProps` will cause an error.                   |
| fieldSchema?        | [`CfnTable.ColumnProperty[]`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnTable.ColumnProperty.html) | User provided schema structure to create an AWS Glue Table.                                                      |
| existingTable?      | [`CfnTable`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnTable.html)                                 | Existing instance of AWS Glue Table. If this is set, tableProps and fieldSchema are ignored.                     |
| tableProps?         | [`CfnTableProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.TableProps.html)                          | User provided AWS Glue Table props to override default props used to create a Glue Table.                        |
| existingDatabase?   | [`CfnDatabase`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnDatabase.html)                           | Existing instance of AWS Glue Database. If this is set, then databaseProps is ignored.                           |
| databaseProps?      | [`CfnDatabaseProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnDatabaseProps.html)                 | User provided Glue Database Props to override the default props used to create the Glue Database.                |
| outputDataStore?    | [`SinkDataStoreProps`](#sinkdatastoreprops)                                                                                   | User provided properties for S3 bucket that stores Glue Job output. Current datastore types supported is only S3. |
|createCloudWatchAlarms?|`boolean`|Whether to create recommended CloudWatch alarms for Kinesis Data Stream. Default value is set to `true`.|
| etlCodeAsset?       | [s3assets.Asset](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3_assets.Asset.html)                               | User provided instance of the Asset class that represents the ETL code on the local filesystem                    |

### SinkDataStoreProps

| **Name**                | **Type**                                                                                          | **Description**                                                                                                |
| :---------------------- | :------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------- |
| existingS3OutputBucket? | [`Bucket`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.Bucket.html)           | Existing instance of S3 bucket where the data should be written. Providing both this and `outputBucketProps` will cause an error. |
| outputBucketProps       | [`BucketProps`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_s3.BucketProps.html) | User provided bucket properties to create the S3 bucket to store the output from the AWS Glue Job.             |
| datastoreType           | [`SinkStoreType`](#sinkstoretype)                                                                 | Sink data store type.                                                                                          |

### SinkStoreType

Enumeration of data store types that could include S3, DynamoDB, DocumentDB, RDS or Redshift. Current construct implementation only supports S3, but potential to add other output types in the future.

| **Name** | **Type** | **Description** |
| :------- | :------- | --------------- |
| S3       | `string` | S3 storage type |

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|kinesisStream|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_kinesis.Stream.html)|Returns an instance of the Kinesis stream created or used by the pattern.|
|glueJob|[`CfnJob`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnJob.html)|Returns an instance of AWS Glue Job created by the construct.|
|glueJobRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_iam.Role.html)|Returns an instance of the IAM Role created by the construct for the Glue Job.|
|database|[`CfnDatabase`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnDatabase.html)|Returns an instance of AWS Glue Database created by the construct.|
|table|[`CfnTable`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_glue.CfnTable.html)|Returns an instance of the AWS Glue Table created by the construct|
|outputBucket?|[`s3.Bucket`](https://docs.aws.amazon.com/cdk/api/latest/docs/aws-s3-readme.html)|Returns an instance of the output bucket created by the construct for the AWS Glue Job.|
|cloudwatchAlarms?|[`cloudwatch.Alarm[]`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudwatch.Alarm.html)|Returns an array of recommended CloudWatch Alarms created by the construct for Kinesis Data stream.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Kinesis Stream

* Configure least privilege access IAM role for Kinesis Stream
* Enable server-side encryption for Kinesis Stream using AWS Managed KMS Key
* Deploy best practices CloudWatch Alarms for the Kinesis Stream

### Glue Job

* Create a Glue Security Config that configures encryption for CloudWatch, Job Bookmarks, and S3. CloudWatch and Job Bookmarks are encrypted using AWS Managed KMS Key created for AWS Glue Service. The S3 bucket is configured with SSE-S3 encryption mode
* Configure service role policies that allow AWS Glue to read from Kinesis Data Streams

### Glue Database

* Create an AWS Glue database. An AWS Glue Table will be added to the database. This table defines the schema for the records buffered in the Amazon Kinesis Data Streams

### Glue Table

* Create an AWS Glue table. The table schema definition is based on the JSON structure of the records buffered in the Amazon Kinesis Data Streams

### IAM Role

* A job execution role that has privileges to 1) read the ETL script from the S3 bucket location, 2) read records from the Kinesis Stream, and 3) execute the Glue Job

### Output S3 Bucket

* An S3 bucket to store the output of the ETL transformation. This bucket will be passed as an argument to the created glue job so that it can be used in the ETL script to write data into it

### Cloudwatch Alarms

* A CloudWatch Alarm to report when consumer application is reading data slower than expected
* A CloudWatch Alarm to report when consumer record processing is falling behind (to avoid risk of data loss due to record expiration)

## Architecture

![Architecture Diagram](architecture.png)

## Reference Implementation

A sample use case which uses this pattern is available under [`use_cases/aws-custom-glue-etl`](https://github.com/awslabs/aws-solutions-constructs/tree/master/source/use_cases/aws-custom-glue-etl).

© Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_glue as _aws_cdk_aws_glue_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kinesis as _aws_cdk_aws_kinesis_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_s3_assets as _aws_cdk_aws_s3_assets_ceddda9d
import aws_solutions_constructs.core as _aws_solutions_constructs_core_ac4f6ab9
import constructs as _constructs_77d1e7e8


class KinesisstreamsToGluejob(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-gluejob.KinesisstreamsToGluejob",
):
    '''
    :summary:

    = This construct either creates or uses the existing construct provided that can be deployed
    to perform streaming ETL operations using:

    - AWS Glue Database
    - AWS Glue Table
    - AWS Glue Job
    - Amazon Kinesis Data Streams
    - Amazon S3 Bucket (output datastore).
    The construct also configures the required role policies so that AWS Glue Job can read data from
    the streams, process it, and write to an output store.
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        database_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        existing_database: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase] = None,
        existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
        existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
        field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        glue_job_props: typing.Any = None,
        kinesis_stream_props: typing.Any = None,
        output_data_store: typing.Optional[typing.Union[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps, typing.Dict[builtins.str, typing.Any]]] = None,
        table_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Constructs a new instance of KinesisstreamsToGluejob.Based on the values set in the.

        :param scope: -
        :param id: -
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param database_props: The props for the Glue database that the construct should use to create. If
        :param etl_code_asset: Provide Asset instance corresponding to the code in the local filesystem, responsible for performing the Glue Job transformation. This property will override any S3 locations provided under glue.CfnJob.JobCommandProperty As of CDK V2, all ETL scripts sourced from local code should explicitly create an asset and provide that asset through this attribute. Default: - None
        :param existing_database: Glue Database for this construct. If not provided the construct will create a new Glue Database. The database is where the schema for the data in Kinesis Data Streams is stored
        :param existing_glue_job: Existing GlueJob configuration. If this property is provided, any properties provided through
        :param existing_stream_obj: Existing instance of Kineses Data Stream. If not set, it will create an instance
        :param existing_table: Glue Table for this construct, If not provided the construct will create a new Table in the database. This table should define the schema for the records in the Kinesis Data Streams. One of
        :param field_schema: Structure of the records in the Amazon Kinesis Data Streams. An example of such a definition is as below. Either Default: - None
        :param glue_job_props: User provides props to override the default props for Glue ETL Jobs. Providing both this and existingGlueJob will cause an error. This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate role policies The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html Default: - None
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used
        :param output_data_store: The output data stores where the transformed data should be written. Current supported data stores include only S3, other potential stores may be added in the future.
        :param table_props: The table properties for the construct to create the table. One of

        :props: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbc920e59dce457bdbc70cc1e178d58faa598ae100339893765113d921508c81)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = KinesisstreamsToGluejobProps(
            create_cloud_watch_alarms=create_cloud_watch_alarms,
            database_props=database_props,
            etl_code_asset=etl_code_asset,
            existing_database=existing_database,
            existing_glue_job=existing_glue_job,
            existing_stream_obj=existing_stream_obj,
            existing_table=existing_table,
            field_schema=field_schema,
            glue_job_props=glue_job_props,
            kinesis_stream_props=kinesis_stream_props,
            output_data_store=output_data_store,
            table_props=table_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> _aws_cdk_aws_glue_ceddda9d.CfnDatabase:
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnDatabase, jsii.get(self, "database"))

    @builtins.property
    @jsii.member(jsii_name="glueJob")
    def glue_job(self) -> _aws_cdk_aws_glue_ceddda9d.CfnJob:
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnJob, jsii.get(self, "glueJob"))

    @builtins.property
    @jsii.member(jsii_name="glueJobRole")
    def glue_job_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "glueJobRole"))

    @builtins.property
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(self) -> _aws_cdk_aws_kinesis_ceddda9d.Stream:
        return typing.cast(_aws_cdk_aws_kinesis_ceddda9d.Stream, jsii.get(self, "kinesisStream"))

    @builtins.property
    @jsii.member(jsii_name="table")
    def table(self) -> _aws_cdk_aws_glue_ceddda9d.CfnTable:
        return typing.cast(_aws_cdk_aws_glue_ceddda9d.CfnTable, jsii.get(self, "table"))

    @builtins.property
    @jsii.member(jsii_name="cloudwatchAlarms")
    def cloudwatch_alarms(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]]:
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudwatch_ceddda9d.Alarm]], jsii.get(self, "cloudwatchAlarms"))

    @builtins.property
    @jsii.member(jsii_name="outputBucket")
    def output_bucket(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Bucket]]:
        '''This property is only set if the Glue Job is created by the construct.

        If an existing Glue Job
        configuration is supplied, the construct does not create an S3 bucket and hence the

        :outputBucket: property is undefined
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_s3_ceddda9d.Bucket]], jsii.get(self, "outputBucket"))


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-gluejob.KinesisstreamsToGluejobProps",
    jsii_struct_bases=[],
    name_mapping={
        "create_cloud_watch_alarms": "createCloudWatchAlarms",
        "database_props": "databaseProps",
        "etl_code_asset": "etlCodeAsset",
        "existing_database": "existingDatabase",
        "existing_glue_job": "existingGlueJob",
        "existing_stream_obj": "existingStreamObj",
        "existing_table": "existingTable",
        "field_schema": "fieldSchema",
        "glue_job_props": "glueJobProps",
        "kinesis_stream_props": "kinesisStreamProps",
        "output_data_store": "outputDataStore",
        "table_props": "tableProps",
    },
)
class KinesisstreamsToGluejobProps:
    def __init__(
        self,
        *,
        create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
        database_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
        etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
        existing_database: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase] = None,
        existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
        existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
        existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
        field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        glue_job_props: typing.Any = None,
        kinesis_stream_props: typing.Any = None,
        output_data_store: typing.Optional[typing.Union[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps, typing.Dict[builtins.str, typing.Any]]] = None,
        table_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param create_cloud_watch_alarms: Whether to create recommended CloudWatch alarms. Default: - Alarms are created
        :param database_props: The props for the Glue database that the construct should use to create. If
        :param etl_code_asset: Provide Asset instance corresponding to the code in the local filesystem, responsible for performing the Glue Job transformation. This property will override any S3 locations provided under glue.CfnJob.JobCommandProperty As of CDK V2, all ETL scripts sourced from local code should explicitly create an asset and provide that asset through this attribute. Default: - None
        :param existing_database: Glue Database for this construct. If not provided the construct will create a new Glue Database. The database is where the schema for the data in Kinesis Data Streams is stored
        :param existing_glue_job: Existing GlueJob configuration. If this property is provided, any properties provided through
        :param existing_stream_obj: Existing instance of Kineses Data Stream. If not set, it will create an instance
        :param existing_table: Glue Table for this construct, If not provided the construct will create a new Table in the database. This table should define the schema for the records in the Kinesis Data Streams. One of
        :param field_schema: Structure of the records in the Amazon Kinesis Data Streams. An example of such a definition is as below. Either Default: - None
        :param glue_job_props: User provides props to override the default props for Glue ETL Jobs. Providing both this and existingGlueJob will cause an error. This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate role policies The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html Default: - None
        :param kinesis_stream_props: User provided props to override the default props for the Kinesis Stream. Default: - Default props are used
        :param output_data_store: The output data stores where the transformed data should be written. Current supported data stores include only S3, other potential stores may be added in the future.
        :param table_props: The table properties for the construct to create the table. One of
        '''
        if isinstance(database_props, dict):
            database_props = _aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps(**database_props)
        if isinstance(output_data_store, dict):
            output_data_store = _aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps(**output_data_store)
        if isinstance(table_props, dict):
            table_props = _aws_cdk_aws_glue_ceddda9d.CfnTableProps(**table_props)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91a198df6179cded6ae11eff1b4291dd59c1d093700b7c0be1e7e553641b564e)
            check_type(argname="argument create_cloud_watch_alarms", value=create_cloud_watch_alarms, expected_type=type_hints["create_cloud_watch_alarms"])
            check_type(argname="argument database_props", value=database_props, expected_type=type_hints["database_props"])
            check_type(argname="argument etl_code_asset", value=etl_code_asset, expected_type=type_hints["etl_code_asset"])
            check_type(argname="argument existing_database", value=existing_database, expected_type=type_hints["existing_database"])
            check_type(argname="argument existing_glue_job", value=existing_glue_job, expected_type=type_hints["existing_glue_job"])
            check_type(argname="argument existing_stream_obj", value=existing_stream_obj, expected_type=type_hints["existing_stream_obj"])
            check_type(argname="argument existing_table", value=existing_table, expected_type=type_hints["existing_table"])
            check_type(argname="argument field_schema", value=field_schema, expected_type=type_hints["field_schema"])
            check_type(argname="argument glue_job_props", value=glue_job_props, expected_type=type_hints["glue_job_props"])
            check_type(argname="argument kinesis_stream_props", value=kinesis_stream_props, expected_type=type_hints["kinesis_stream_props"])
            check_type(argname="argument output_data_store", value=output_data_store, expected_type=type_hints["output_data_store"])
            check_type(argname="argument table_props", value=table_props, expected_type=type_hints["table_props"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create_cloud_watch_alarms is not None:
            self._values["create_cloud_watch_alarms"] = create_cloud_watch_alarms
        if database_props is not None:
            self._values["database_props"] = database_props
        if etl_code_asset is not None:
            self._values["etl_code_asset"] = etl_code_asset
        if existing_database is not None:
            self._values["existing_database"] = existing_database
        if existing_glue_job is not None:
            self._values["existing_glue_job"] = existing_glue_job
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if existing_table is not None:
            self._values["existing_table"] = existing_table
        if field_schema is not None:
            self._values["field_schema"] = field_schema
        if glue_job_props is not None:
            self._values["glue_job_props"] = glue_job_props
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props
        if output_data_store is not None:
            self._values["output_data_store"] = output_data_store
        if table_props is not None:
            self._values["table_props"] = table_props

    @builtins.property
    def create_cloud_watch_alarms(self) -> typing.Optional[builtins.bool]:
        '''Whether to create recommended CloudWatch alarms.

        :default: - Alarms are created
        '''
        result = self._values.get("create_cloud_watch_alarms")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def database_props(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps]:
        '''The props for the Glue database that the construct should use to create.

        If

        :database: and
        :databaseprops:

        is provided, the
        construct will define a GlueDatabase resource.
        '''
        result = self._values.get("database_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps], result)

    @builtins.property
    def etl_code_asset(self) -> typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset]:
        '''Provide Asset instance corresponding to the code in the local filesystem, responsible for performing the Glue Job transformation.

        This property will override any S3 locations provided
        under glue.CfnJob.JobCommandProperty

        As of CDK V2, all ETL scripts sourced from local code should explicitly create an asset and provide
        that asset through this attribute.

        :default: - None
        '''
        result = self._values.get("etl_code_asset")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset], result)

    @builtins.property
    def existing_database(
        self,
    ) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase]:
        '''Glue Database for this construct.

        If not provided the construct will create a new Glue Database.
        The database is where the schema for the data in Kinesis Data Streams is stored
        '''
        result = self._values.get("existing_database")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase], result)

    @builtins.property
    def existing_glue_job(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob]:
        '''Existing GlueJob configuration.

        If this property is provided, any properties provided through

        :KinesisstreamsToGluejobProps: .etlCodeAsset will take higher precedence and override the JobCommandProperty.scriptLocation
        :glueJobProps:

        is ignored.
        The ETL script can be provided either under glue.CfnJob.JobCommandProperty or set as an Asset instance under
        '''
        result = self._values.get("existing_glue_job")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob], result)

    @builtins.property
    def existing_stream_obj(
        self,
    ) -> typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream]:
        '''Existing instance of Kineses Data Stream.

        If not set, it will create an instance
        '''
        result = self._values.get("existing_stream_obj")
        return typing.cast(typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream], result)

    @builtins.property
    def existing_table(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable]:
        '''Glue Table for this construct, If not provided the construct will create a new Table in the database.

        This table should define the schema for the records in the Kinesis Data Streams.
        One of

        :fieldSchema: is ignored
        :table: is provided,
        :tableprops: is provided then
        '''
        result = self._values.get("existing_table")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable], result)

    @builtins.property
    def field_schema(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty]]:
        '''Structure of the records in the Amazon Kinesis Data Streams.

        An example of such a  definition is as below.
        Either

        :default: - None

        :fieldSchema:

        is ignored
        "FieldSchema": [{
        "name": "id",
        "type": "int",
        "comment": "Identifier for the record"
        }, {
        "name": "name",
        "type": "string",
        "comment": "The name of the record"
        }, {
        "name": "type",
        "type": "string",
        "comment": "The type of the record"
        }, {
        "name": "numericvalue",
        "type": "int",
        "comment": "Some value associated with the record"
        },
        :table: is provided then
        '''
        result = self._values.get("field_schema")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty]], result)

    @builtins.property
    def glue_job_props(self) -> typing.Any:
        '''User provides props to override the default props for Glue ETL Jobs.

        Providing both this and
        existingGlueJob will cause an error.

        This parameter is defined as ``any`` to not enforce passing the Glue Job role which is a mandatory parameter
        for CfnJobProps. If a role is not passed, the construct creates one for you and attaches the appropriate
        role policies

        The default props will set the Glue Version 2.0, with 2 Workers and WorkerType as G1.X. For details on
        defining a Glue Job, please refer the following link for documentation - https://docs.aws.amazon.com/glue/latest/webapi/API_Job.html

        :default: - None
        '''
        result = self._values.get("glue_job_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def kinesis_stream_props(self) -> typing.Any:
        '''User provided props to override the default props for the Kinesis Stream.

        :default: - Default props are used
        '''
        result = self._values.get("kinesis_stream_props")
        return typing.cast(typing.Any, result)

    @builtins.property
    def output_data_store(
        self,
    ) -> typing.Optional[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps]:
        '''The output data stores where the transformed data should be written.

        Current supported data stores
        include only S3, other potential stores may be added in the future.
        '''
        result = self._values.get("output_data_store")
        return typing.cast(typing.Optional[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps], result)

    @builtins.property
    def table_props(self) -> typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTableProps]:
        '''The table properties for the construct to create the table.

        One of

        :fieldSchema: is ignored
        :table: is provided,
        :tableprops: is provided then
        '''
        result = self._values.get("table_props")
        return typing.cast(typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTableProps], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KinesisstreamsToGluejobProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KinesisstreamsToGluejob",
    "KinesisstreamsToGluejobProps",
]

publication.publish()

def _typecheckingstub__dbc920e59dce457bdbc70cc1e178d58faa598ae100339893765113d921508c81(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
    database_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    existing_database: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase] = None,
    existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
    existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
    field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    glue_job_props: typing.Any = None,
    kinesis_stream_props: typing.Any = None,
    output_data_store: typing.Optional[typing.Union[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps, typing.Dict[builtins.str, typing.Any]]] = None,
    table_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a198df6179cded6ae11eff1b4291dd59c1d093700b7c0be1e7e553641b564e(
    *,
    create_cloud_watch_alarms: typing.Optional[builtins.bool] = None,
    database_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnDatabaseProps, typing.Dict[builtins.str, typing.Any]]] = None,
    etl_code_asset: typing.Optional[_aws_cdk_aws_s3_assets_ceddda9d.Asset] = None,
    existing_database: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnDatabase] = None,
    existing_glue_job: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnJob] = None,
    existing_stream_obj: typing.Optional[_aws_cdk_aws_kinesis_ceddda9d.Stream] = None,
    existing_table: typing.Optional[_aws_cdk_aws_glue_ceddda9d.CfnTable] = None,
    field_schema: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTable.ColumnProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    glue_job_props: typing.Any = None,
    kinesis_stream_props: typing.Any = None,
    output_data_store: typing.Optional[typing.Union[_aws_solutions_constructs_core_ac4f6ab9.SinkDataStoreProps, typing.Dict[builtins.str, typing.Any]]] = None,
    table_props: typing.Optional[typing.Union[_aws_cdk_aws_glue_ceddda9d.CfnTableProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
