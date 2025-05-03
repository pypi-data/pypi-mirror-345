import os
import sys
import boto3
import botocore.exceptions as be
from boto3.s3.transfer import TransferConfig
import json
from tqdm import tqdm
from .Logging import Debug  # Import logging class
from .Config import Config  # Import config class

class ProgressPercentage:
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._tqdm = tqdm(total=self._size, unit='B', unit_scale=True, desc=filename)

    def __call__(self, bytes_amount):
        self._seen_so_far += bytes_amount
        self._tqdm.update(bytes_amount)

class AWSIntegration:
    """Static AWS Helper Class for managing S3 and Secrets Manager operations."""

    s3_client = None
    secret_client = None
    _current_profile = None

    @staticmethod
    def initialize(profile: str = "default", verbose: bool = False):
        """Initializes AWS clients for S3 and Secrets Manager.

        If credentials are missing, prompts the user for input. If authentication
        fails, resets credentials so that `initialize()` can be called again for reattempt.
        Args:
            aws_profile (str, optional): Specifies which AWS profile to use for the connection. Defaults to 'Default' profile.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.
        Raises:
            Exception: If AWS authentication fails or Default profile not found in .toml file.
        """

        # If already initialized successfully, return
        if AWSIntegration.s3_client is not None and AWSIntegration.secret_client is not None:
            Debug.log(f"Already authenticated! using profile: '{AWSIntegration._current_profile}'!", 'DEBUG', verbose)
            return  
        
        try:
            aws_creds   = Config.get_aws_credentials(profile=profile)  # Change "default" to "production" as needed
            access_key  = aws_creds["AWS_ACCESS_KEY"]
            secret_key  = aws_creds["AWS_SECRET_KEY"]
            region      = aws_creds["REGION"]
        
        except TypeError as e:
            Debug.log(f"No profile named '{profile}' in config file.", 'ERROR')
            sys.exit(1)

        try:
            identity = AWSIntegration.check_connection(access_key, secret_key, region)
            AWSIntegration._current_profile = profile # Persist the currently authenticated profile

            Debug.log(f"Authenticated as: {identity['Arn'].split('/')[-1]}", 'SUCCESS')

        except be.ClientError as e:
            Debug.log("Invalid credentials. Please verify that your profile has the required permissions.", 'ERROR')
            sys.exit(1) 


        try:

            AWSIntegration.s3_client = boto3.client(
                "s3",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            AWSIntegration.secret_client = boto3.client(
                "secretsmanager",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
            
            Debug.log(f"Successfully created connection to aws clients!", 'DEBUG', verbose)

        except be.ClientError as e:
            error_code = e.response['Error']['Code']
            # Reset class variables to allow retrying on next call
            AWSIntegration.s3_client = None
            AWSIntegration.secret_client = None

            # Reset environment variables (so `initialize()` prompts again on next call)
            os.environ.pop("AWS_ACCESS_KEY_ID", None)
            os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
            
            if error_code == 'InvalidAccessKeyId':
                Debug.log(f"\n\nThe selected IAM user is not found.\n", 'ERROR')
            
    @staticmethod
    def check_connection(access_key: str, secret_key: str, region: str):
        '''Validates connection to AWS by fetching the caller identity.
            Args:
                access_key (str): The IAM access key associated with the IAM user.
                secret_key (str): The IAM access key associated with the IAM user.
            Returns:
                identity (boto3.client.identity): The called identity, IF authenticated.
        '''
        try:
            sts_client = boto3.client(
                "sts",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )
        
        except be.ClientError as e:
            Debug.log(f"Invalid credentials, verify you are using the correct IAM profile.", 'ERROR')

        identity = sts_client.get_caller_identity()

        return identity

    @staticmethod
    def define_s3_transfer_config(size_threshold: float, threads: int):
        """Defines and returns an AWS S3 TransferConfig for efficient file uploads.

        Args:
            size_threshold (float): The file size (in GB) at which multipart upload should trigger.
            threads (int): Number of concurrent threads for upload.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Returns:
            TransferConfig: Configured transfer settings for AWS S3 uploads.
        """
        GB = 1024 ** 3
        Debug.log(f"Threshold for multithreaded upload to S3: {size_threshold}GB\n"
                f"Concurrent threads: {threads}", 'INFO')

        return TransferConfig(multipart_threshold=size_threshold * GB, max_concurrency=threads)

    @staticmethod
    def get_secret(secret_name: str, verbose: bool = False):
        """Retrieves a secret from AWS Secrets Manager.

        Args:
            secret_name (str): The name of the secret to retrieve.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Returns:
            dict: The secret's value parsed as a dictionary.

        Raises:
            Exception: If retrieval fails.
        """
        if AWSIntegration.s3_client is None or AWSIntegration.secret_client is None:
            Debug.log("AWS clients not initialized. Please call 'initialize()' before using this method.", 'ERROR')
            return
        
        try:
            response = AWSIntegration.secret_client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            Debug.log(f"Failed to retrieve secret: {e}", 'ERROR')

    @staticmethod
    def get_bucket_contents(bucket_name: str, verbose: bool = False):
        """Lists all files in a given AWS S3 bucket.

        Args:
            bucket_name (str): The name of the S3 bucket.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Returns:
            list[str]: A list of filenames stored in the bucket.

        Raises:
            Exception: If the bucket is not accessible.
        """
        if AWSIntegration.s3_client is None or AWSIntegration.secret_client is None:
            Debug.log("AWS clients not initialized. Please call 'initialize()' before using this method.", 'ERROR')
            return

        try:
            response = AWSIntegration.s3_client.list_objects_v2(Bucket=bucket_name)
            return [item['Key'] for item in response.get('Contents', [])]
        
        except be.ParamValidationError as e:
            Debug.log(f"Cannot list objects within a single folder. See 'list_objects_in_folder' method.", 'ERROR')

        except Exception as e:
            Debug.log(f"Error fetching bucket contents: {e}", 'ERROR')
            
    @staticmethod
    def push_file_to_s3(bucket_name: str, file_to_upload: str, key: str, config: TransferConfig = None, verbose: bool = False):
        """Uploads a file to an AWS S3 bucket.

        Args:
            bucket_name (str): The destination S3 bucket name.
            file_to_upload (str): Path to the file to upload.
            key (str): The S3 key (filename) to assign.
            config (TransferConfig, optional): AWS S3 transfer configuration. Defaults to None.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Raises:
            Exception: If the upload fails.
        """
        if AWSIntegration.s3_client is None or AWSIntegration.secret_client is None:
            Debug.log("AWS clients not initialized. Please call 'initialize()' before using this method.", 'ERROR')
            return

        if config is None:
            config = AWSIntegration.define_s3_transfer_config(0.1, 10)

        try:
            Debug.log(f"Uploading {file_to_upload} to {bucket_name}/{key}...", 'INFO')

            with open(file_to_upload, 'rb') as file_obj:
                AWSIntegration.s3_client.upload_fileobj(
                    file_obj, bucket_name, key, Config=config, Callback=ProgressPercentage(file_to_upload)
                )

            Debug.log(f"Successfully uploaded {file_to_upload} to {bucket_name}/{key}", 'SUCCESS')

        except Exception as e:
            Debug.log(f"Error uploading file: {e}", 'ERROR')