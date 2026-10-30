import logging
from typing import Any, Dict, Optional
import boto3
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)


def get_dynamodb_table():
    """Obtains the DynamoDB Table resource using AWS IAM credentials."""
    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    return dynamodb.Table(settings.DYNAMODB_TABLE_NAME)


def save_url(short_code: str, original_url: str, created_at: str) -> Dict[str, Any]:
    """Saves a shortened URL record in DynamoDB."""
    table = get_dynamodb_table()
    item = {
        "short_code": short_code,
        "original_url": original_url,
        "created_at": created_at,
    }
    try:
        table.put_item(Item=item)
        return item
    except ClientError as e:
        logger.error(f"Error saving to DynamoDB: {e.response['Error']['Message']}")
        raise e


def get_url(short_code: str) -> Optional[Dict[str, Any]]:
    """Retrieves a URL record by short_code from DynamoDB."""
    table = get_dynamodb_table()
    try:
        response = table.get_item(Key={"short_code": short_code})
        return response.get("Item")
    except ClientError as e:
        logger.error(f"Error querying DynamoDB: {e.response['Error']['Message']}")
        raise e
