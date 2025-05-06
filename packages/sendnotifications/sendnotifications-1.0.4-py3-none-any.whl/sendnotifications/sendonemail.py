import json
import logging
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)
class NotifyEmail:
    """Core NotifyEmail Class.
       Usage:

        from sendnotifications.sendonemail import NotifyEmail
        message = ""
        NotifyEmail(title="Title - Testing card",message_body=messages,recipeint="vthelu")

        Parameters:
             title: str - Subject
             messages:str - message
             recipient: str - Recepient Team Identifier

       Send Messages to subscribed email address"""
    __topic_name_ = "sendnotification-sharedlib-sns-notify-email-events"
    __topcic_arn_ = ""

    def __init__(self, title: str, message_body: str, recepient: str = None, message_attr: str = None) -> None:
        self.__topcic_arn_ = self.__get_topic_arn_(self.__topic_name_)
        self.__send_message_to_email_(title=title, message_body=message_body, recepient=recepient,
                                      message_attr=message_attr)

    def __send_message_to_email_(self, title: str, message_body: str, recepient: str = None,
                                 message_attr: str = None) -> None:
        client = boto3.client("sns")

        if not message_attr:
            message_attr = {'Team': {'StringValue': recepient, 'DataType': 'String'}}
        response = client.publish(TargetArn=self.__topcic_arn_, Message=json.dumps(message_body), Subject=title,
                                  MessageAttributes=message_attr)
        print(response)
        logger.info('Status Code: {}'.format(response.status_code))
        logger.info('Response: {}'.format(response.content))

    def __get_topic_arn_(self, topic_name: str):
        sns_client = boto3.client('sns')
        sts_client = boto3.client('sts')

        try:
            caller_identity = sts_client.get_caller_identity()
            account_id = caller_identity['Account']
            response = sns_client.get_topic_attributes(
                TopicArn=f"arn:aws:sns:{sns_client.meta.region_name}:{account_id}:{topic_name}")
            return response['Attributes']['TopicArn']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NotFoundException':
                return None
            else:
                raise e
