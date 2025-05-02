# Amazon S3 Tables Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Amazon S3 Tables

Amazon S3 Tables deliver the first cloud object store with built-in Apache Iceberg support and streamline storing tabular data at scale.

[Product Page](https://aws.amazon.com/s3/features/tables/) | [User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)

## Usage

### Define an S3 Table Bucket

```python
# Build a Table bucket
sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
    table_bucket_name="example-bucket-1",
    # optional fields:
    unreferenced_file_removal=UnreferencedFileRemoval(
        status=UnreferencedFileRemovalStatus.ENABLED,
        noncurrent_days=20,
        unreferenced_days=20
    )
)
```

Learn more about table buckets maintenance operations and default behavior from the [S3 Tables User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html)

### Controlling Table Bucket Permissions

```python
# Grant the principal read permissions to the bucket and all tables within
account_id = "123456789012"
table_bucket.grant_read(iam.AccountPrincipal(account_id), "*")
# Grant the role write permissions to the bucket and all tables within
role = iam.Role(stack, "MyRole", assumed_by=iam.ServicePrincipal("sample"))
table_bucket.grant_write(role, "*")
# Grant the user read and write permissions to the bucket and all tables within
table_bucket.grant_read_write(iam.User(stack, "MyUser"), "*")

# Grant permissions to the bucket and a particular table within it
table_id = "6ba046b2-26de-44cf-9144-0c7862593a7b"
table_bucket.grant_read_write(iam.AccountPrincipal(account_id), table_id)

# Add custom resource policy statements
permissions = iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    actions=["s3tables:*"],
    principals=[iam.ServicePrincipal("example.aws.internal")],
    resources=["*"]
)

table_bucket.add_to_resource_policy(permissions)
```

## Coming Soon

L2 Construct support for:

* Namespaces
* Tables
