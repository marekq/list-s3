list_s3
=========

List all file objects stored in S3 buckets attached to an AWS account using AWS API keys. 

Description
------------

The list_s3 tool can be used to create timestamped CSV reports about files stored within S3 buckets of an AWS account. This is helpful if you are a user of multiple S3 buckets with nested folders which becomes a bit difficult using just the AWS console view. Using the reports it becomes easy to review files stored in buckets, including information about the owner, access permissions and modification times. 

Example output is shown below;

| bucket       | object-name            | object-size  | bucket-region  | bucket-owner  | bucket-permission  | storage-type  | bucket-create-date  | bucket-create-unix  | file-create-date  | file-create-unix | 
|--------------|------------------------|--------------|----------------|---------------|--------------------|---------------|---------------------|---------------------|-------------------|------------------|
| marek.rocks  | index.html             | 211613       | eu-west-1      | marekq        | FULL_CONTROL       | STANDARD      | 2016-06-05_03-00    | 1465092040          | 2016-06-03_21-36  | 1464986192       | 
| marek.rocks  | papers.html            | 899          | eu-west-1      | marekq        | FULL_CONTROL       | STANDARD      | 2016-06-05_03-00    | 1465092040          | 2016-06-03_21-36  | 1464986192       | 
| marek.rocks  | papers/                | 0            | eu-west-1      | marekq        | FULL_CONTROL       | STANDARD      | 2016-06-05_03-00    | 1465092040          | 2016-06-03_21-36  | 1464986206       |
| marek.rocks  | papers/lia.pdf         | 1472885      | eu-west-1      | marekq        | FULL_CONTROL       | STANDARD      | 2016-06-05_03-00    | 1465092040          | 2016-06-03_21-36  | 1464986206       |
| marek.rocks  | papers/ot.pdf          | 476803       | eu-west-1      | marekq        | FULL_CONTROL       | STANDARD      | 2016-06-05_03-00    | 1465092040          | 2016-06-03_21-36  | 1464986207       |
| ...          | ...                    | ...          | ...            | ...           | ...                | ...           | ...                 | ...                 | ...               | ...              |


Installation
------------

The tool has been tested on Debian, but should work on other platforms too. Besides Python, install the following package using 'python-pip';

    $ pip install boto3 

Next, edit the 'creds.py' file to include your AWS API credentials as follows;

    aws_access_key_id           = 'accesskeygoeshere'
    aws_secret_access_key       = 'secretkeygoeshere'
    region_name                 = 'regiongoeshere'

You can run 'python list_s3.py' to check if the tool works well on your machine and if valid credentials were entered. As an alternative, you can also submit credentials as arguments which can be useful if you want a one time report;

        $ python list_s3.py <aws_access_key> <aws_secret_access_key> <region_name>

Usage
-----

The tool picks up credentials configured in 'creds.py' in the folders root. 

    $ python list_s3.py

Results of the scan are shown on screen and stored in "results.csv" in the current directory, in addition a timestamped copy of the results file is stored in folder 'results' in the current directory.

AWS permissions
---------------

It is recommended to create a readonly AWS IAM account specifically for usage with this tool using a minimal amount of priviledges - you don't want someone to read the actual file contents or delete all files if the keys ever get stolen. Never use your root credentials for these kind of reports, always use specific roles for them. 

I recommend to use the following policy document;
        
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetBucketAcl",
                    "s3:GetBucketLocation",
                    "s3:GetBucketPolicy",
                    "s3:GetBucketWebsite",
                    "s3:ListAllMyBuckets",
                    "s3:GetObjectAcl",
                    "s3:ListBucket",
                    "s3:ListObjects"
                ],
                "Resource": [
                    "arn:aws:s3:::*"
                ]
            }
        ]
    }
        

Contact
-------

For any questions or fixes, please reach out to @marekq! 
