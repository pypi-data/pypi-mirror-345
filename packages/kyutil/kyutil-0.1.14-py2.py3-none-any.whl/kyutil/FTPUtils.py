# -*- coding: UTF-8 -*-
"""FTPUtils.py"""
import ftplib
import ssl


class ReusedSslSocket(ssl.SSLSocket):
    def unwrap(self):
        pass


# MyFTP_TLS is derived to support TLS_RESUME(filezilla server)
class MyFtpTLS(ftplib.FTP_TLS):
    """Explicit FTPS, with shared TLS session"""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(
                conn,
                server_hostname=self.host,
                session=self.sock.session)

            conn.__class__ = ReusedSslSocket

        return conn, size
