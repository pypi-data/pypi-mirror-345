## keyring provider for octoDNS

An [octoDNS](https://github.com/octodns/octodns/) secrets handler that targets [keyring](https://pypi.org/project/keyring/).

### Installation

#### Command line

```
pip install octodns-keyring
```

#### requirements.txt/setup.py

Pinning specific versions or SHAs is recommended to avoid unplanned upgrades.

##### Versions

```
# Start with the latest versions and don't just copy what's here
octodns==0.9.14
octodns-keyring==0.0.1
```

##### SHAs

```
# Start with the latest/specific versions and don't just copy what's here
-e git+https://git@github.com/octodns/octodns.git@9da19749e28f68407a1c246dfdf65663cdc1c422#egg=octodns
-e git+https://git@github.com/octodns/octodns-keyring.git@ec9661f8b335241ae4746eea467a8509205e6a30#egg=octodns_keyring
```

### Configuration

```yaml
secret_handlers:
  keyring:
    class: octodns_keyring.KeyringSecrets
    # The keyring backend to use (optional.) If omitted keyrings built-in
    # process will apply
    backend: keyring.backends.null.Keyring
    # Any other key and value pairs will be assigned to attributes on the
    # backend once it's been created. (optional)
    some_backend_property: 42

providers:
  route53:
    class: octodns_route53.Ec2Source
    access_key_id: keyring/octodns/AWS_ACCESS_KEY_ID
    secret_access_key: keyring/octodns/AWS_SECRET_ACCESS_KEY
    region: us-east-1
```

### Development

See the [/script/](/script/) directory for some tools to help with the development process. They generally follow the [Script to rule them all](https://github.com/github/scripts-to-rule-them-all) pattern. Most useful is `./script/bootstrap` which will create a venv and install both the runtime and development related requirements. It will also hook up a pre-commit hook that covers most of what's run by CI.
