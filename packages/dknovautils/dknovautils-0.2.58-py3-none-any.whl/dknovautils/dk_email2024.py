from getpass import getpass

import json
from typing import Protocol

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from dknovautils import AT
from dknovautils import *


from email.message import EmailMessage

import smtplib, ssl


class EmailUtils:
    """
    https://realpython.com/python-send-email/






    """

    @classmethod
    def rnd_str(cls) -> str:
        return str(AT.fepochMillis())

    @classmethod
    def ssh_email_file(
        cls,
        server: str,
        user: str,
        passwd: str,
        from_id: str,
        to_id: str,
        dirpath: str,
        subject: str,
        message: str,
        port=22,
    ):
        """
        todo

        from_id, to_id:
            a-zA-Z0-9-

        subject 过滤算法



        """

        # pip install scp
        from scp import SCPClient

        import paramiko
        from scp import SCPClient

        # pip install scp

        # cmd = f'sudo mkdir -p "{dirpath}"; '
        # f_ssh(ip=server, user=username, pwd=pwd, port=port, cmd=cmd)

        fname = f"{cls.rnd_str()}.email.txt"
        infofile = DkFile(f"/tmp/{fname}")
        ctt = f"subject:{subject} msg:{message}"
        infofile.path.write_text(data=ctt, encoding="utf-8")

        tfname = f"{from_id}_{to_id}_{AT.sdf_isocompact_format_datetime()}_subject.email.txt"  # todo

        def createSSHClient(server, port, user, password):
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server, port, user, password)
            return client

        ssh = createSSHClient(server, port, user, passwd)
        scp = SCPClient(ssh.get_transport())
        scp.put(
            infofile.pathstr,
            remote_path=f"{dirpath}/{tfname}",
            preserve_times=True,
        )

        # todo remove infofile

        pass

    @classmethod
    def send_mail_v2024(
        cls,
        mode: str,
        server: str,
        from_email: str,
        to_email,
        subject,
        message,
        password: str,
        username: str | None = None,
        port=465,
    ):
        """

        如果密码错误 会在login的时候出现错误
        比如 Connection unexpectedly closed


        """

        if not username:
            username = from_email

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(to_email)
        msg.set_content(message)
        print(msg)

        if mode == "a":
            # Create a secure SSL context
            context = ssl.create_default_context()
            with smtplib.SMTP(server, port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(username, password)
                # TODO: Send email here
                server.send_message(msg)

        elif mode == "ssl_b":

            smtp = smtplib.SMTP_SSL(server)  # 此处直接一步到位
            smtp.login(username, password)  # 登录SMTP服务
            smtp.send_message(msg)  # 通过SMTP服务器发送邮件
            smtp.quit()

        else:
            AT.never("err94645 bad mode")

        iprint_info("successfully sent the mail.")

        """
        
参考代码
https://www.cnblogs.com/zjdxr-up/p/17872354.html
  
        
20250107 如下代码发送邮件成功

        两个邮箱的授权码都要登录管理一下。长期不用最好重新生成授权码。

        pwd = "xxx"
        EmailUtils.send_mail_v2024(
            mode="b",
            server="smtp.163.com",
            from_email="xxxx@163.com",
            password=pwd,
            to_email=["xxxx@outlook.com", "xxxx@qq.com"],
            subject=f"hello {millis} 大家好 ",
            message=f"Your analysis has done! {millis} 大家好 ",
        )   
        
        pwd = "xxx"
        EmailUtils.send_mail_v2024(
            mode="b",
            server="smtp.qq.com",
            from_email="xxxx@qq.com",
            password=pwd,
            to_email=["xxxx@outlook.com", "xxxx@outlook.com"],
            subject=f"hello {millis} 大家好 ",
            message=f"Your analysis has done! {millis} 大家好 ",
        )             
        
        """

    @classmethod
    def f_send_email(cls):
        AT.unimplemented()
        pass

    """
    

def send_single_email(to_address: str, subject: str, message: str):
    try:
        api_key = os.getenv("MAILGUN_API_KEY")  # get API-Key from the `.env` file

        resp = requests.post(MAILGUN_API_URL, auth=("api", api_key),
                             data={"from": FROM_EMAIL_ADDRESS,
                                   "to": to_address, "subject": subject, "text": message})
        if resp.status_code == 200:  # success
            logging.info(f"Successfully sent an email to '{to_address}' via Mailgun API.")
        else:  # error
            logging.error(f"Could not send the email, reason: {resp.text}")

    except Exception as ex:
        logging.exception(f"Mailgun error: {ex}")

if __name__ == "__main__":
    send_single_email("Manish <manish@exanple.com>", "Single email test", "Testing Mailgun API for a single email")    
    
    

        
    """


"""

这个事情极其无聊，就是smtp经常不能正常工作。
https://www.cnblogs.com/zjdxr-up/p/17872354.html



https://www.emailtooltester.com/en/blog/free-smtp-servers/


https://app.courier.com/
    用gmail帐号登录
    
    似乎也不知道如何简单上手使用。
    
    Your complete platform for sending notifications

    10,000 messages per month for free, no credit card required.
    
    
    curl --request POST \
    --url https://api.courier.com/send \
    --header 'Authorization: Bearer YOUR_AUTH_TOKEN_HERE' \
    --data '{
        "message": {
        "to": {"email":"xxxx@gmail.com"},
        "template": "xxxxxxxx",
        "data": {"recipientName":"hellobaby"}
        }
    }'    




"""
