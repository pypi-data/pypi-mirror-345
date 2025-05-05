from typing import Any

from string import Template

from ka_uts_aod.aodpath import AoDPath
from ka_uts_log.log import LogEq

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import smtplib

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[dict[Any, Any]]
TnAny = None | Any


class MailSnd:
    """
    Send Email
    """
    @staticmethod
    def add_attachements(msg, aopath, kwargs) -> None:
        for _path in aopath:
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


class MailDoSnd:
    """
    Send Email
    """
    @staticmethod
    def create(d_snd: TyDic):
        _from = d_snd.get('from', '')
        _to = d_snd.get('to', '')
        _subject = d_snd.get('subject', '')
        _cc = d_snd.get('cc', '')
        _bcc = d_snd.get('bcc', '')
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

    @classmethod
    def send(cls, d_snd: TyDic, kwargs: TyDic) -> None:
        LogEq.debug("_d_snd", d_snd)
        _msg = cls.create(d_snd)

        _aod_path: TyAoD = d_snd.get('paths', [])
        _aopath: TyArr = AoDPath.sh_aopath(_aod_path, kwargs)

        _a_body: TyArr = d_snd.get('body', [])
        LogEq.debug("_a_body", _a_body)
        _body: str = '\n'.join(_a_body)
        LogEq.debug("_body", _body)
        LogEq.debug("_aopath", _aopath)
        # _body_template = Template(_body)
        # _body = _body_template.safe_substitute(*_aopath)
        _body = _body.format(*_aopath)
        LogEq.debug("_body", _body)

        _msg.attach(MIMEText(_body, 'plain'))

        _sw_attachements: TyAoD = d_snd.get('sw_attachements', False)
        if _sw_attachements:
            MailSnd.add_attachements(_msg, _aopath, kwargs)

        # Send the email
        MailSnd.send(_msg, d_snd)
