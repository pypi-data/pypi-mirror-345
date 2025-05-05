import requests
import requests.adapters
import winreg
from winreg import OpenKey, QueryValueEx
from requests_kerberos import HTTPKerberosAuth, OPTIONAL
from pypac import PACSession, get_pac
from urllib.parse import urlparse

class PyProxSession():
    def __init__(self):
        pac_location = self.get_pac_location()
        self.pac = get_pac(url=pac_location, allowed_content_types="application/octet-stream")
        session1 = PACSession(self.pac)
        proxies = session1._proxy_resolver.get_proxy_for_requests('https://google.com')
        self.http_proxy = proxies['http']
        self.proxysession = requests.Session()
        self.proxysession.proxies = proxies
        self.proxysession.mount('https://', self.ProxySessionMount())

    def get_pac_location(self):
        with OpenKey(
            winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"
        ) as key1:
            pac_string = QueryValueEx(key1, "AutoConfigURL")
            return pac_string[0]
        
    class ProxySessionMount(requests.adapters.HTTPAdapter):
        def proxy_headers(self, proxyurl):
            auth = HTTPKerberosAuth()
            auth_token = auth.generate_request_header(None, urlparse(proxyurl).hostname, is_preemptive=True)
            headers = {"Proxy-Authorization" : auth_token}
            return headers

