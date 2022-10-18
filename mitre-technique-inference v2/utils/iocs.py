import iocextract
from typing import Dict, List
from msticpy.transform import IoCExtract as msticpy_iocextract

class IocPipeline():
    '''
    Extract IOCs from cyber threat intel data.
    
    IOCs supported -
    - ip (ipv4/ipv6)
    - dns
    - url
    - md5_hash
    - sha1_hash
    - sha256_hash
    - sha512_hash
    - email
    - yara
    - path (Windows/Linux)
    '''
    
    def __init__(self):
        self.iocs = {}
        self.msticpy_ioc_extractor = msticpy_iocextract()

    def go(self, data: str, refang: bool = False):
        self.msticpy_iocs = dict(self.msticpy_ioc_extractor.extract(data, include_paths = True))
        self._get_iocs(data, refang=refang)
        for key, values in self.iocs.items():
            self.iocs[key] = list(filter(None, values))
        return self.iocs       

    def _get_iocs(self, data: str, refang: bool):
        self.iocs['IP']             = self._get_ips(data, refang)
        self.iocs['EMAIL']          = self._get_emails(data, refang)
        self.iocs['URL']            = self._get_urls(data, refang)
        self.iocs['YARA']           = self._get_yara(data)
        self.iocs['MD5_HASH']       = self._get_md5(data)
        self.iocs['SHA1_HASH']      = self._get_sha1(data)
        self.iocs['SHA256_HASH']    = self._get_sha256(data)
        self.iocs['SHA512_HASH']    = self._get_sha512(data)
        self.iocs['DNS']            = self._get_dns(data)
        self.iocs['PATH']           = self._get_path(data)

    def _get_ips(self, data: str, refang: bool):
        all_ips = []
        iocextract_ips = list(iocextract.extract_ips(data, refang=refang))
        iocextract_ipv4s = list(iocextract.extract_ipv4s(data, refang=refang))
        iocextract_ipv6s = list(iocextract.extract_ipv6s(data))
        all_ips += iocextract_ips + iocextract_ipv4s + iocextract_ipv6s

        if 'ipv4' in self.msticpy_iocs.keys():
            all_ips += list(self.msticpy_iocs['ipv4'])
        
        if 'ipv6' in self.msticpy_iocs.keys():
            all_ips += list(self.msticpy_iocs['ipv6'])
        
        return list(set(all_ips))
        
    
    def _get_emails(self, data: str, refang: bool):
        iocextract_emails = list(iocextract.extract_emails(data, refang=refang))
        return sorted(list(set(iocextract_emails)), key=len, reverse=True)

    def _get_yara(self, data: str):
        iocextract_yara = list(iocextract.extract_yara_rules(data))
        return list(set(iocextract_yara))

    def _get_urls(self, data: str, refang: bool):
        all_urls = []
        iocextract_encoded_urls = list(iocextract.extract_encoded_urls(data, refang=refang))
        iocextract_unencoded_urls = list(iocextract.extract_unencoded_urls(data, refang=refang))
        iocextract_urls = list(iocextract.extract_urls(data, refang=refang))
        all_urls += iocextract_encoded_urls + iocextract_unencoded_urls + iocextract_urls

        if 'url' in self.msticpy_iocs.keys():
            all_urls += list(self.msticpy_iocs['url'])
        
        return list(set(all_urls))

    def _get_md5(self, data: str):
        all_md5 = []
        iocextract_md5 = list(iocextract.extract_md5_hashes(data))
        all_md5 += iocextract_md5

        if 'md5_hash' in self.msticpy_iocs.keys():
            all_md5 += list(self.msticpy_iocs['md5_hash'])

        return list(set(all_md5))
        

    def _get_sha1(self, data: str):
        all_sha1 = []
        iocextract_sha1 = list(iocextract.extract_sha1_hashes(data))
        all_sha1 += iocextract_sha1

        if 'sha1_hash' in self.msticpy_iocs.keys():
            all_sha1 += list(self.msticpy_iocs['sha1_hash'])
        
        return list(set(all_sha1))

    def _get_sha256(self, data: str):
        all_sha256 = []
        iocextract_sha256 = list(iocextract.extract_sha256_hashes(data))
        all_sha256 += iocextract_sha256

        if 'sha256_hash' in self.msticpy_iocs.keys():
            all_sha256 += list(self.msticpy_iocs['sha256_hash'])

        return list(set(all_sha256))
    
    def _get_sha512(self, data: str):
        iocextract_sha512 = list(iocextract.extract_sha512_hashes(data))
        return list(set(iocextract_sha512))
    
    def _get_dns(self, data: str):
        all_dns = []

        if 'dns' in self.msticpy_iocs.keys():
            all_dns += list(self.msticpy_iocs['dns'])

        return list(set(all_dns))

    def _get_path(self, data: str):
        all_paths = []

        if 'windows_path' in self.msticpy_iocs.keys():
            all_paths += list(self.msticpy_iocs['windows_path'])
        
        if 'linux_path' in self.msticpy_iocs.keys():
            all_paths += list(self.msticpy_iocs['linux_path'])
        
        return all_paths
    
    @staticmethod
    def reverse(iocs):
        reversed_dict = {}
        for key, values in iocs.items():
            if isinstance(values, list):
                for value in sorted(values, key=len, reverse=True):
                    reversed_dict[value] = key + '_TOKEN'
            elif isinstance(values, str):
                reversed_dict[values] = key + '_TOKEN'
            else:
                continue
        return reversed_dict