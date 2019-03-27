from email.mime.text import MIMEText
import boto3

from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError


def send_raw_email(to_email, reply_to, subject, message):
    SENDER = "Pam Report <no-reply@app.usepam.com>"
    msg = MIMEMultipart()
    msg.set_charset("utf-8")
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = to_email
    msg['Reply-to'] = reply_to

    msg.attach(MIMEText(message))

    # attachmensts
    # XXX remove hard coded client
    client = boto3.client(
        'ses', aws_access_key_id='AKIAIHFAW4CMLKGZJWQQ',
        aws_secret_access_key='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',
        region_name='us-east-1')
    print(
        client.send_raw_email(
            RawMessage={'Data': msg.as_string()},
            Source=SENDER, Destinations=[to_email]))


# send_raw_email("aaronorosen@gmail.com", 'aaronorose.n@gmail.com',
#               'subject', 'message')

def send_email(to_email, subject, message):
    SENDER = "Pam Report <no-reply@app.usepam.com>"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = to_email

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = message

    # The character encoding for the email.
    CHARSET = "UTF-8"
    ACCESS_KEY = 'AKIAIHFAW4CMLKGZJWQQ'
    SECRET_KEY = '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'

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',
                          aws_access_key_id=ACCESS_KEY,
                          aws_secret_access_key=SECRET_KEY,
                          region_name=AWS_REGION)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
