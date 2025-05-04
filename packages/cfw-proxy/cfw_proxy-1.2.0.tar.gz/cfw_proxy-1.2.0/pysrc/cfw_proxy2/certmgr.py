from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime
import uuid
from threading import Lock
import os
import os.path
import ipaddress

# from .logconfig import get_logger

def create_ca(lasting_days=3650, keyfile="ca.key", cafile="ca.crt"):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'CFW Proxy CA'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'CFW Proxy'),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u'DO NOT TRUST'),
    ])
    
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)     # issuer should be the same as subject to meet the CA requirements
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.today() - datetime.timedelta(1, 0, 0))
        .not_valid_after(datetime.datetime.today() + datetime.timedelta(lasting_days, 0, 0))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None), 
            critical=True,
        )
        .add_extension(x509.KeyUsage(
                key_cert_sign=True,         # CA can sign other certificates
                crl_sign=False,
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
            ), 
            critical=True
        )
        .add_extension(x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]), 
            critical=True
        )
    )
    
    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    with open(keyfile, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(cafile, "wb") as f:
        f.write(certificate.public_bytes(
            encoding=serialization.Encoding.PEM,
        ))


def require_cert(domains, cakey_file, cacrt_file):
    # generate private key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # generate CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"CFW Proxy"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"hack-by-cfw-proxy.com"),
    ])).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(domain) for domain in domains]),
        critical=False,
    ).sign(key, hashes.SHA256(), default_backend())
    
    # load CA 
    with open(cakey_file, "rb") as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
    with open(cacrt_file, "rb") as f:
        ca_crt = x509.load_pem_x509_certificate(f.read(), default_backend())
    
    # sign CSR
    csr_ext = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    cert = (
        x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(ca_crt.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.today() - datetime.timedelta(1, 0, 0))
            .not_valid_after(datetime.datetime.today() + datetime.timedelta(365 * 3, 0, 0))
            .add_extension(
                csr_ext.value,
                csr_ext.critical,
            )
            .sign(ca_key, hashes.SHA256(), default_backend())
    )
    
    
    cert_bytes = cert.public_bytes(serialization.Encoding.PEM)
    key_bytes = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    return (cert_bytes, key_bytes)


def is_ip_address(domain):
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False


class CertCache:
    def __init__(self, cache_dir='./cert_cache', cafile='ca.crt', cakey='ca.key') -> None:
        self.__cache = {}  # domain -> (cert_path, key_path)
        self.cache_dir = cache_dir
        
        self.cafile = cafile
        self.cakey = cakey
        
        # self.logger = get_logger("CertCache")
        
        self.__load_cert()
        self.__lock = Lock()
    
    def __load_cert(self):
        if not os.path.exists(self.cache_dir):
            return
        
        filenames = os.listdir(self.cache_dir)
        for name in filenames:
            if name.endswith(".crt"):
                if name.endswith(".ip.crt"):
                    basename = name[:-7]
                    key_name = basename + ".ip.key"
                    domain = basename.replace("_", ".")
                elif name.endswith(".ipv6.crt"):
                    basename = name[:-9]
                    key_name = basename + ".ipv6.key"
                    domain = basename.replace("_", ":")
                else:
                    basename = name[:-4]
                    key_name = basename + ".key"
                    domain = basename

                key_path = os.path.join(self.cache_dir, key_name)
                if not os.path.exists(key_path):
                    # self.logger.warning(f'{key_name} not found, skip {basename}')
                    continue
                if domain not in self.__cache:
                    cert_path = os.path.realpath(os.path.join(self.cache_dir, name))
                    key_path = os.path.realpath(key_path)
                    self.__cache[domain] = (cert_path, key_path)
    
    
    def __find(self, domain):
        if domain in self.__cache:
            # self.logger.debug(f"CertCache: hit for {domain}")
            return self.__cache[domain]
        
        if is_ip_address(domain):
            return None, None
        
        # find wildcard cert
        parts = domain.split(".")
        domain = ".".join(parts[1:])
        if domain in self.__cache:
            # self.logger.debug(f"CertCache: hit for {domain}")
            return self.__cache[domain]
        
        return None, None
    

    def get_cert(self, domain):
        """
        For example, let the domain be "baidu.com". Returns a path to the cert 
        file and key file ("baidu.com.crt", "baidu.com.key"). The cert file has 
        the cert for "baidu.com" and "*.baidu.com".
        
        If the domain is "www.baidu.com", find the cert for "baidu.com" and 
        return it.
        
        If the domain is "abc.www.baidu.com", find the cert for "*.www.baidu.com"
        and return it if "www.baidu.com.crt" exists. Otherwise, create the cert.
        
        If the domain is a IP address, get a cert for it, which has no wildcard.
        """
        
        with self.__lock:
            cer_path, key_path = self.__find(domain)
            if cer_path: return cer_path, key_path
            
            # self.logger.debug(f"CertCache: miss for {domain}")
            SAN_domains = []
            cert_name = None
            if is_ip_address(domain):
                SAN_domains = [domain]
                if "." in domain:
                    cert_name = domain.replace(".", "_") + ".ip"
                else:
                    cert_name = domain.replace(":", "_") + ".ipv6"
            else:
                parts = domain.split(".")
                if len(parts) <= 2:
                    SAN_domains = [domain, "*." + domain]
                    cert_name = domain
                else:
                    super_domain = ".".join(parts[1:])
                    SAN_domains = [super_domain, "*." + super_domain]
                    cert_name = super_domain
            
            # self.logger.debug(f"CertCache: create cert {cert_name} for {SAN_domains}")
            (cert_bytes, key_bytes) = require_cert(SAN_domains, self.cakey, self.cafile)
            cert_path = os.path.realpath(os.path.join(self.cache_dir, cert_name + ".crt"))
            key_path = os.path.realpath(os.path.join(self.cache_dir, cert_name + ".key"))
            with open(cert_path, "wb") as f:
                f.write(cert_bytes)
            with open(key_path, "wb") as f:
                f.write(key_bytes)
            
            self.__cache[domain] = (cert_path, key_path)
            return cert_path, key_path

    def clear(self):
        with self.__lock:
            self.__cache.clear()
            for name in os.listdir(self.cache_dir):
                if name.endswith(".crt") or name.endswith(".key"):
                    os.remove(os.path.join(self.cache_dir, name))
        

if __name__ == "__main__":
    create_ca()