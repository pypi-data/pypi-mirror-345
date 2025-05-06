from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, FastMail, MessageType
from pydantic import EmailStr



def _build_mail_client() -> FastMail:
    from webserver.config import settings
    return FastMail(settings.smtp_config)


def _build_client_args(subject: str,
                       recipients: list[EmailStr | str],
                       body: dict | str,
                       template: str,
                       cc_recipients: list[EmailStr | str] | None = None,
                       bcc_recipients: list[EmailStr | str] | None = None,
                       reply_to_recipients: list[EmailStr | str] | None = None
                       ) -> dict[str, object]:
    """
    Build all required arguments to send a message via e-mail.
    # TODO: add support for attachments
    # https://github.com/sabuhish/fastapi-mail/blob/master/docs/example.md#customizing-attachments-by-headers-and-mime-type

    :param subject: message subject
    :param recipients: targets
    :param body: key-value pairs of variables to be injected into the message via templating
    :param template: message template available under `TEMPLATES_FOLDER`
    :param cc_recipients: list of carbon-copy recipients
    :param bcc_recipients: list of black carbon-copy recipients
    :param reply_to_recipients: list of recipients to reply to
    :return:
    """
    args: dict = {}
    message_schema: dict = {
        "subject": subject,
        "recipients": recipients,
        "cc": cc_recipients or [],
        "bcc": bcc_recipients or [],
        "reply_to": reply_to_recipients or []
    }

    # --- build body-related fields on message schema
    if type(body) == str:
        if str(body).startswith("<html>"):
            message_schema["subtype"] = MessageType.html
        else:
            message_schema["subtype"] = MessageType.plain

        message_schema["body"] = body
    elif template:
        message_schema["subtype"] = MessageType.html
        message_schema["template_body"] = body
        args["template_name"] = template

    # build message schema
    args["message"] = MessageSchema(**message_schema)

    return args


async def send_email_async(subject: str,
                           recipients: list[EmailStr | str],
                           body: dict | None,
                           template: str | None = None,
                           cc_recipients: list[EmailStr | str] | None = None,
                           bcc_recipients: list[EmailStr | str] | None = None,
                           reply_to_recipients: list[EmailStr | str] | None = None):
    """
    Send an e-mail asynchronously.

    :param subject: message subject
    :param recipients: targets
    :param body: key-value pairs of variables to be injected into the message via templating
    :param template: message template available under `TEMPLATES_FOLDER`
    :param cc_recipients: list of carbon-copy recipients
    :param bcc_recipients: list of black carbon-copy recipients
    :param reply_to_recipients: list of recipients to reply to
    """
    await _build_mail_client().send_message(
        **_build_client_args(subject, recipients, body, template, cc_recipients, bcc_recipients, reply_to_recipients)
    )


def send_email_background(background_tasks: BackgroundTasks,
                          subject: str,
                          recipients: list[EmailStr | str],
                          body: dict,
                          template: str,
                          cc_recipients: list[EmailStr | str] | None = None,
                          bcc_recipients: list[EmailStr | str] | None = None,
                          reply_to_recipients: list[EmailStr | str] | None = None):
    """
    Send an e-mail in background.

    :param subject: message subject
    :param recipients: targets
    :param body: key-value pairs of variables to be injected into the message via templating
    :param template: message template available under `TEMPLATES_FOLDER`
    :param cc_recipients: list of carbon-copy recipients
    :param bcc_recipients: list of black carbon-copy recipients
    :param reply_to_recipients: list of recipients to reply to
    """
    background_tasks.add_task(_build_mail_client().send_message,
                              **_build_client_args(subject, recipients, body, template, cc_recipients, bcc_recipients,
                                                   reply_to_recipients))
