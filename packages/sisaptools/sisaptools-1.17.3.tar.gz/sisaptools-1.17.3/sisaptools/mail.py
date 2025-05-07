# -*- coding: utf8 -*-

"""
Utilitats per enviar mails.
"""

import smtplib
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
import json
from os.path import basename
import socket

from .constants import APP_CHARSET, IS_PYTHON_3
from .aes import AESCipher
from .services import MAIL_SERVERS
from .ssh import SFTP


class Mail(object):
    """Classe principal a instanciar."""

    def __init__(self, server="gencat"):
        """Inicialització de paràmetres."""
        self.srv = MAIL_SERVERS[server]['host']
        self.port = MAIL_SERVERS[server]['port']
        self.ssl = MAIL_SERVERS[server]['ssl']
        self.usr = MAIL_SERVERS[server]['user']
        self.pwd = MAIL_SERVERS[server]['password']
        self.me = MAIL_SERVERS[server]['me']
        self.to = []
        self.cc = []
        self.subject = ''
        self.text = ''
        self.attachments = []

    def __construct(self):
        """Construcció del missatge, cridat per send."""
        banned = ("mmedinap@gencat.cat",)
        self.to = [el for el in self.to if el not in banned]
        self.cc = [el for el in self.cc if el not in banned]
        self.message = MIMEMultipart()
        self.message['From'] = self.me
        self.message['To'] = COMMASPACE.join(self.to)
        self.message['Cc'] = COMMASPACE.join(self.cc)
        self.message['Date'] = formatdate(localtime=True)
        self.message['Subject'] = Header(self.subject, APP_CHARSET)
        self.message.attach(MIMEText(self.text, 'plain', APP_CHARSET))
        for _attachment in self.attachments:
            if type(_attachment) in (list, tuple):
                filename, iterable = _attachment
                data = '\r\n'.join([';'.join(map(str, row)) for row in iterable])  # noqa
                attachment = MIMEText(data, 'plain', APP_CHARSET)
                attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=filename
                )
            else:
                filename = _attachment
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(open(filename, 'rb').read())
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment; filename="{}"'.format(basename(filename)))  # noqa
            self.message.attach(attachment)
        self.to += self.cc

    def __connect(self):
        """Connexió al servidor, cridat per send."""
        method = smtplib.SMTP_SSL if self.ssl else smtplib.SMTP
        self.server = method(self.srv, self.port)
        try:
            self.server.login(self.usr, AESCipher().decrypt(self.pwd))
        except Exception:
            pass

    def send(self):
        """Enviament del mail."""
        if self.to or self.cc:
            if IS_PYTHON_3:
                self.__construct()
                self.__connect()
                self.server.sendmail(self.me, self.to, self.message.as_string())  # noqa
                self.server.close()
            else:
                self.send_to_socket()

    def send_to_socket(self):
        """
        Finals 2024 deixa de funcionar gencat en python2 (és filtre
        d'entrada, no de sortida, perquè a destinataris externs arriba).
        Durant unes setmanes funciona amb gmail però de seguida falla pel
        mateix filtre d'entrada.
        """
        # attachments a sftp
        attach = []
        for attachment in self.attachments:
            if type(attachment) not in (list, tuple):
                nom = attachment.split("/")[-1]
                SFTP("sisap").put(attachment, nom)
                attach.append(nom)
        # enviem
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("10.80.217.84", 53008))
        data = {"to": self.to, "cc": self.cc, "subject": self.subject,
                "text": self.text,
                "attachments": attach if attach else self.attachments}
        dades = [data, "fi_de_la_transmissio"]
        data_json = json.dumps(dades, ensure_ascii=False)
        s.sendall(data_json)
        # rebem
        received_json = ""
        while True:
            packet = s.recv(4096)
            if not packet:
                break
            received_json += packet
            if '"fi_de_la_transmissio"]' in received_json:
                break
        result = json.loads(received_json)[0]
        s.close()
        if result != "enviat":
            raise BaseException(result)
