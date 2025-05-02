from setuptools import setup

setup(
    name='certbot-dns-dnsprivacy',
    version='0.3.0',
    packages=['certbot_dns_dnsprivacy'],
    install_requires=['certbot>=2.0.0', 'requests'],
    entry_points={
        'certbot.plugins': [
            'dns-dnsprivacy = certbot_dns_dnsprivacy.dns_dnsprivacy:Authenticator',
        ],
    },
)
