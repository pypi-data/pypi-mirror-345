# certbot-dns-dnsprivacy

`certbot-dns-dnsprivacy` is a Certbot plugin that automates the process of creating and cleaning up DNS TXT records for domain validation using the UK DNS Privacy Project API.

## Installation

To install the package, use the following command:

```bash
pip install certbot-dns-dnsprivacy
```

## Usage

This plugin allows Certbot to perform DNS-01 challenges using the UK DNS Privacy Project API. Below is an example of how to use it:

1. Create a `credentials.ini` file with the following content:

   ```ini
   # credentials.ini
   dns_dnsprivacy_token = YOUR_API_TOKEN
   ```

   Replace `YOUR_API_TOKEN` with your API token from the [UK DNS Privacy Project API settings](https://dnsprivacy.org.uk/settings/api_keys).

2. Run Certbot with the following command:

   ```bash
   certbot certonly \
     --authenticator dns-dnsprivacy \
     --dns-dnsprivacy-credentials ./credentials.ini \
     --dns-dnsprivacy-propagation-seconds 60 \
     -d example.com
   ```

   Replace `example.com` with your domain name.

## Development

To set up a development environment:

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the package in editable mode:

   ```bash
   pip install -e .
   ```

4. Run the test script:

   ```bash
   ./test.sh
   ```

## Contributing

If you would like to contribute to this project, please fork the repository, create a feature branch, and submit a pull request. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Links

- [Homepage](https://dnsprivacy.org.uk/)
- [Issues](https://github.com/UK-DNS-Privacy-Project/certbot-dns-dnsprivacy/issues)