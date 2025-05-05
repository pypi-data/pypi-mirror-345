#
#
#

from importlib import import_module

from keyring import get_keyring

from octodns.secret.base import BaseSecrets
from octodns.secret.exception import SecretsException

# TODO: remove __VERSION__ with the next major version release
__version__ = __VERSION__ = '1.0.0'


class KeyringSecretsException(SecretsException):
    pass


class KeyringSecretsBackendException(KeyringSecretsException):
    pass


class KeyringSecrets(BaseSecrets):
    def __init__(self, name, backend=None, **kwargs):
        super().__init__(name)
        self.backend = self._load_backend(backend)

        for k, v in kwargs.items():
            setattr(self.backend, k, v)

    def _load_backend(self, backend):
        if backend is None:
            return get_keyring()

        try:
            module_name, class_name = backend.rsplit('.', 1)
            module = import_module(module_name)
        except (ImportError, ValueError):
            self.log.exception(
                '_load_backend: Unable to import module "%s"', backend
            )
            raise KeyringSecretsBackendException(
                f'Unknown backend class: "{backend}"'
            )

        try:
            klass = getattr(module, class_name)
        except AttributeError:
            self.log.exception(
                '__init__: Unable to get class "%s" from module "%s"',
                class_name,
                module,
            )
            raise KeyringSecretsBackendException(
                f'Unknown backend class: "{backend}"'
            )

        return klass()

    def _parse_name(self, name):
        return name.split('/')

    def set(self, name, value):
        service_name, secret_name = self._parse_name(name)
        self.backend.set_password(service_name, secret_name, value)

    def fetch(self, name, source):
        service_name, secret_name = self._parse_name(name)
        val = self.backend.get_password(service_name, secret_name)
        if val is None:
            raise KeyringSecretsException(f'failed to find {name}')
        if isinstance(val, str):
            try:
                if '.' in val:
                    # there's a ., try as a float
                    val = float(val)
                else:
                    # otherwise see if we can make an int of it
                    val = int(val)
            except:
                # didn't work, leave it as-is, a string
                pass
        return val

    def delete(self, name):
        service_name, secret_name = self._parse_name(name)
        self.backend.delete_password(service_name, secret_name)
