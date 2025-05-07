hash=$(openssl x509 -noout -hash -in /etc/grid-security/ca.pem)

mkdir -pv /etc/grid-security/certificates
update-ca-trust force-enable

cp -fv /etc/grid-security/ca.pem  /etc/pki/ca-trust/source/anchors/rucio-ca.pem
update-ca-trust extract
ls -lotr /etc/pki/tls/certs/ca-bundle.crt

# TODO: avoid attempt copying the certificate if it already exists
cp -fv /etc/grid-security/ca.pem /etc/grid-security/certificates/$hash.0 || echo "Certificate already exists"
