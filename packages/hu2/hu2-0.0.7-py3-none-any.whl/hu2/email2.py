from email.utils import make_msgid,formatdate
from email.message import EmailMessage
import smtplib

def get_email_head(email: str) -> str:
    """
    获取合法邮箱的头部，形如 abc@qq.com -> abc   \n
    不合法的字符串原样返回，if not x 返回 空串
    """
    if not email: return ''
    sep_idx = email.find('@')
    if sep_idx == -1:
        return email
    else:
        return email[:sep_idx]


class Email:
    def __init__(self, sender_email: str, sender_password: str, receivers_email: list[str],*, subject: str,content:str):
        self.sender_email = sender_email
        self.receivers_email = receivers_email
        self.sender_password = sender_password
        self.message = EmailMessage()
        self.message['Subject'] = subject
        self.message['From'] = '{} <{}>'.format(get_email_head(self.sender_email),self.sender_email)
        self.message['To'] = ', '.join(['{} <{}>'.format(get_email_head(email),email) for email in self.receivers_email])

        self.message['Date'] = formatdate(usegmt=True)
        self.message['Message-ID'] = make_msgid()
        # X-Mailer 这个邮件头 非常重要，否则 139邮箱向其他邮箱发送会失败
        self.message['X-Mailer'] = "Microsoft Outlook Express 6.00.2900.2869"

        self.message.set_content(content)


    def send(self, smtp_host: str, smtp_port: int=25):
        """
        向服务器发送邮件
        :return: 如果多个收件人都成功，返回空字典，否则 按照收件人 返回失败信息。 与smtp.sendmail()返回值一致。
        """
        ret: dict[str, tuple[int, bytes]]
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.login(self.sender_email, self.sender_password)
            ret = smtp.sendmail(self.sender_email, self.receivers_email, self.message.as_string())

        return ret




