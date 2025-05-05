import boto3
import datetime
from decimal import Decimal
from typing import Optional, List

from ephor_cli.conversation_server.types import Conversation


class DDBManager:
    """DynamoDB implementation of the ApplicationManager interface

    This class uses DynamoDB to store and retrieve conversation data.
    """

    def __init__(self, table_name: str, region: str = "us-east-1"):
        """Initialize the DDB Manager with a table name.

        Args:
            table_name: The name of the DynamoDB table
            region: AWS region for the DynamoDB table
        """
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def _get_pk(self, user_id: str, project_id: str) -> str:
        """Create the partition key for a conversation."""
        return f"USER#{user_id}#PROJECT#{project_id}#CONVERSATIONS"

    def _get_sk(self, conversation_id: str) -> str:
        """Create the sort key for a conversation."""
        return f"CONVERSATION#{conversation_id}"

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """Store a conversation in DynamoDB.

        Args:
            conversation: The conversation object to store

        Returns:
            The same conversation object
        """
        # Convert Pydantic model to dict
        conversation_dict = conversation.model_dump()

        # Add DynamoDB keys and timestamps
        item = {
            "PK": self._get_pk(conversation.user_id, conversation.project_id),
            "SK": self._get_sk(conversation.conversation_id),
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat(),
            **conversation_dict,
        }

        # Store in DynamoDB
        self.table.put_item(Item=item)
        return conversation

    def update_conversation(
        self, user_id: str, project_id: str, conversation_id: str, updates: dict
    ) -> bool:
        """Update an existing conversation in DynamoDB.

        This method allows updating specific fields of a conversation without
        requiring the entire Conversation object.

        Args:
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to
            conversation_id: The ID of the conversation to update
            updates: Dictionary of fields to update and their new values

        Returns:
            True if the update was successful, False otherwise
        """
        if not updates:
            return False

        print("Updating conversation", updates)

        # Build update expression dynamically
        update_expression_parts = ["SET updated_at = :updated_at"]
        expression_attr_values = {":updated_at": datetime.datetime.utcnow().isoformat()}
        expression_attr_names = {}

        # Add each field to the update expression
        for key, value in updates.items():
            # Sanitize for DynamoDB
            value = self.sanitize_for_dynamodb(value)

            update_expression_parts.append(f"#{key} = :{key}")
            expression_attr_values[f":{key}"] = value
            expression_attr_names[f"#{key}"] = key

        update_expression = ", ".join(update_expression_parts)

        try:
            result = self.table.update_item(
                Key={
                    "PK": self._get_pk(user_id, project_id),
                    "SK": self._get_sk(conversation_id),
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attr_names,
                ExpressionAttributeValues=expression_attr_values,
            )
            print("Result", result)
            return True
        except Exception as e:
            print(f"DynamoDB update_conversation error: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def sanitize_for_dynamodb(self, data):
        """
        Recursively sanitize data for DynamoDB by converting Pydantic models to dicts
        and floats to Decimal.
        """
        # Handle None
        if data is None:
            return None

        # Handle Pydantic models
        if hasattr(data, "model_dump"):
            print(f"Converting Pydantic model to dict: {type(data)}")
            return self.sanitize_for_dynamodb(data.model_dump())

        # Handle float values - convert to Decimal for DynamoDB
        if isinstance(data, float):
            return Decimal(str(data))

        # Handle lists and tuples
        if isinstance(data, (list, tuple)):
            return [self.sanitize_for_dynamodb(item) for item in data]

        # Handle dictionaries
        if isinstance(data, dict):
            return {
                key: self.sanitize_for_dynamodb(value) for key, value in data.items()
            }

        # Return other data types as is
        return data

    def get_conversation(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> Optional[Conversation]:
        """Get a conversation by ID.

        Args:
            conversation_id: The ID of the conversation to retrieve
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to

        Returns:
            The conversation if found, None otherwise
        """
        response = self.table.get_item(
            Key={
                "PK": self._get_pk(user_id, project_id),
                "SK": self._get_sk(conversation_id),
            }
        )

        if "Item" not in response:
            return None

        # Remove DynamoDB-specific fields
        item = response["Item"]
        for key in ["PK", "SK"]:
            if key in item:
                del item[key]
        # Use Pydantic to convert dict to Conversation
        return Conversation.model_validate(item)

    def list_conversations(self, user_id: str, project_id: str) -> List[Conversation]:
        """List all conversations for a user and project.

        Args:
            user_id: The ID of the user who owns the conversations
            project_id: The ID of the project the conversations belong to

        Returns:
            A list of conversations
        """
        response = self.table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": self._get_pk(user_id, project_id)},
        )

        conversations = []
        for item in response.get("Items", []):
            # Remove DynamoDB-specific fields
            for key in ["PK", "SK"]:
                if key in item:
                    del item[key]
            # Use Pydantic to convert dict to Conversation
            conversations.append(Conversation.model_validate(item))

        return conversations

    def delete_conversation(
        self, conversation_id: str, project_id: str, user_id: str
    ) -> bool:
        """Delete a conversation by ID.

        Args:
            conversation_id: The ID of the conversation to delete
            user_id: The ID of the user who owns the conversation
            project_id: The ID of the project the conversation belongs to

        Returns:
            True if the conversation was deleted, False otherwise
        """
        try:
            self.table.delete_item(
                Key={
                    "PK": self._get_pk(user_id, project_id),
                    "SK": self._get_sk(conversation_id),
                }
            )
            return True
        except Exception:
            return False
