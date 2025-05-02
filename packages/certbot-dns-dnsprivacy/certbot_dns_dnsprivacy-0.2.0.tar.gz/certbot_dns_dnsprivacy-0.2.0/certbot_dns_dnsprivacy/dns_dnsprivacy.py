import logging
import requests

from certbot import errors, interfaces
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

API_BASE = "https://dnsprivacy.org.uk/domains"
ACCOUNT_URL = "https://dnsprivacy.org.uk/settings/api_keys"

class Authenticator(dns_common.DNSAuthenticator):
    """DNS Authenticator for dnsprivacy.org.uk API"""

    description = 'Create TXT records using the dnsprivacy.org.uk API'
    ttl = 60

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None
        self._record_ids = {}  # Store record IDs for cleanup

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add, 
            default_propagation_seconds=10)
        add('credentials', help='UK DNS Privacy Project credentials INI file.')

    def more_info(self):
        return 'This plugin creates TXT records via the dnsprivacy.org.uk DNS API.'

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'UK DNS Privacy Project credentials INI file',
            {
                'token': 'User access token for the UK DNS Privacy Project API. '
                '(See {0}.)'.format(ACCOUNT_URL)
            }
        )

    def _perform(self, domain, validation_name, validation):
        self._create_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain, validation_name, validation):
        self._delete_txt_record(domain, validation_name, validation)

    def _create_txt_record(self, domain, record_name, value):
        token = self.credentials.conf('token')

        logger.debug(f"Using token: {token}")

        url = f"{API_BASE}/{domain}/records"
        headers = {
            'Authorization': f"Bearer {token}",
            'accept': 'application/json',
            'content-type': 'application/json'
        }

        name = record_name
        if name.endswith('.' + domain):
            name = name[:-len(domain) - 1]
        
        data = {
            "name": name,
            "record_type": "TXT",
            "content": value,
            "ttl": self.ttl
        }

        logger.debug(f"POST to {url} with data {data}")
        response = requests.post(url, headers=headers, json=data)
        if not response.ok:
            raise errors.PluginError(f"Error creating DNS record: {response.text}")
        
        try:
            record_id = response.json().get('id')
            if record_id:
                # Store the record ID for later cleanup
                key = (domain, record_name, value)
                self._record_ids[key] = record_id
                logger.debug(f"Stored record ID {record_id} for {key}")
            else:
                logger.warning("No record ID returned from API")
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to parse record ID from response: {e}")

    def _delete_txt_record(self, domain, record_name, value):
        key = (domain, record_name, value)
        record_id = self._record_ids.get(key)
        
        if not record_id:
            logger.warning(f"No record ID found for {key}, skipping deletion")
            return
        
        token = self.credentials.conf('token')
        url = f"{API_BASE}/{domain}/records/{record_id}"
        headers = {'Authorization': f"Bearer {token}"}
        
        logger.debug(f"DELETE request to {url}")
        response = requests.delete(url, headers=headers)
        
        if response.ok:
            logger.debug(f"Successfully deleted DNS record with ID {record_id}")
            # Remove the record ID from our dictionary
            self._record_ids.pop(key, None)
        else:
            logger.warning(f"Failed to delete DNS record with ID {record_id}: {response.text}")
