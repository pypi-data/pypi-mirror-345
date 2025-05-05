#!/usr/bin/env python
'''
Octo-DNS keyring tool
'''

from argparse import ArgumentParser
from getpass import getpass

from octodns_keyring import KeyringSecrets


def main():
    parser = ArgumentParser(description=__doc__.split('\n')[1])

    parser.add_argument(
        '--backend',
        required=False,
        help='The keyring backend to use (optional.) If omitted keyrings built-in process will apply',
    )
    parser.add_argument(
        '--backend-args',
        nargs='*',
        required=False,
        help='Backend configation, attributes to be assign on the backend once created. Format key1=val1 key2=val. "--" will end ... args',
    )
    parser.add_argument(
        '--fetch',
        action='store_true',
        default=False,
        required=False,
        help='Fetch and print the existing values',
    )
    parser.add_argument(
        '--delete',
        action='store_true',
        default=False,
        required=False,
        help='Delete existing secrets',
    )
    parser.add_argument(
        'names',
        nargs='*',
        help='Values to set in the keyring backend. Format service_name/secret_name, e.g. octodns/ns1_api_key. Multiple secrets are space seperated. User will be prompted for the value of each',
    )

    args = parser.parse_args()

    kwargs = {}
    for backend_arg in args.backend_args or []:
        k, v = backend_arg.split('=')
        kwargs[k] = v

    ks = KeyringSecrets('octodns-keyring', args.backend, **kwargs)

    for name in args.names:
        if args.fetch:
            value = ks.fetch(name, None)
            print(f'{name}={value}')
        elif args.delete:
            ks.delete(name)
            print(f'{name} *deleted*')
        else:
            value = getpass(f'{name}: ')
            ks.set(name, value)


if __name__ == '__main__':
    main()
