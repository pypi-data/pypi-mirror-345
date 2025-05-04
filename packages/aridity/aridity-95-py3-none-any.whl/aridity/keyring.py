from .model import Scalar
from .util import null_exc_info
from base64 import b64decode
from functools import partial
from getpass import getpass
from subprocess import CalledProcessError, check_output
from tempfile import NamedTemporaryFile
from threading import Semaphore
import logging, os

log = logging.getLogger(__name__)
passwordbase = str
setenvonce = Semaphore()

class Password(passwordbase):

    def __new__(cls, password, setter):
        p = passwordbase.__new__(cls, password)
        p.setter = setter
        return p

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self.setter is not None and null_exc_info == exc_info:
            self.setter(self)

def keyring(scope, serviceres, usernameres):
    if scope.resolved('keyring_cron').scalar and setenvonce.acquire(False):
        key = 'DBUS_SESSION_BUS_ADDRESS'
        value = f"unix:path=/run/user/{os.geteuid()}/bus"
        log.debug("Set %s to: %s", key, value)
        os.environ[key] = value
    from keyring import get_password, set_password
    service = serviceres.resolve(scope).textvalue
    username = usernameres.resolve(scope).textvalue
    password = None if scope.resolved('keyring_force').scalar else get_password(service, username)
    return Scalar(Password(*[getpass(), partial(set_password, service, username)] if password is None else [password, None]))

class DecryptionFailedException(Exception): pass

def gpg(scope, resolvable):
    'Use gpg to decrypt the given base64-encoded blob.'
    with NamedTemporaryFile() as f:
        f.write(b64decode(resolvable.resolve(scope).textvalue))
        f.flush()
        try:
            return Scalar(Password(check_output(['gpg', '-d', f.name]).decode('ascii'), None))
        except CalledProcessError:
            raise DecryptionFailedException
