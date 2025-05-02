from typing import Any

from ka_uts_dic.dopath import DoPath
from ka_uts_log.log import LogEq

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
# from email.mime.text import MIMEText
from email import encoders
import smtplib

TyDic = dict[Any, Any]
TnAny = None | Any


class MailSnd:
    """ Send Email
    """
    @staticmethod
    def create(d_send: TyDic):
        _from = d_send.get('from', '')
        _to = d_send.get('to', '')
        _subject = d_send.get('subject', '')
        _cc = d_send.get('cc', '')
        _bcc = d_send.get('bcc', '')
        # Create the email
        _msg = MIMEMultipart()
        _msg['From'] = _from
        _msg['To'] = _to
        _msg['Subject'] = _subject
        if _cc:
            _msg['Cc'] = _cc
        if _bcc:
            _msg['Bcc'] = _bcc
        return _msg

    @staticmethod
    def add_attachements(msg, aod_path, kwargs) -> None:
        # _body = d_send.get('body')
        # msg.attach(MIMEText(_body, 'plain'))
        for _d_path in aod_path:
            _path = DoPath.sh_path(_d_path, kwargs)
            LogEq.debug("_d_path", _d_path)
            LogEq.debug("_path", _path)

            # Attach the file
            _attachment = MIMEBase('application', 'octet-stream')
            with open(_path, 'rb') as fd:
                _attachment.set_payload(fd.read())
            encoders.encode_base64(_attachment)
            _attachment.add_header(
                    'Content-Disposition', f'attachment; filename={_path}')
            msg.attach(_attachment)

    @staticmethod
    def send(msg, d_send: TyDic) -> None:
        _from: str = d_send.get('from', '')
        _host: str = d_send.get('host', '')
        _password: str = d_send.get('password', '')
        _sw_ssl: bool = d_send.get('sw_ssl', True)
        if _sw_ssl:
            _port = d_send.get('ssl_port', 465)
            with smtplib.SMTP_SSL(_host, _port) as smtp:
                smtp.login(_from, _password)
                smtp.send_message(msg)
                smtp.quit()
        else:
            _port = d_send.get('tls_port', 587)
            with smtplib.SMTP(_host, _port) as smtp:
                smtp.starttls()
                smtp.login(_from, _password)
                smtp.send_message(msg)
                smtp.quit()
