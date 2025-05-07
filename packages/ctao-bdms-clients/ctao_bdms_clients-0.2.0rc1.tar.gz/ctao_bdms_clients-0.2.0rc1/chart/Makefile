install:
	helm upgrade --install --wait bdms .

test:
	helm test bdms

publish:
	helm package .
	helm push bdms-0.1.0.tgz oci://harbor.cta-observatory.org/dpps

reset:
	helm delete bdms || true
	kubectl delete secrets bdms-rucio-server bdms-rucio-server-tls bdms-server-cafile bdms-server-hostcert bdms-server-hostkey dppsuser-certkey || true
	kubectl delete job  generate-certificates configure-test-rucio test-rucio || true
	kubectl delete pvc data-bdms-postgresql-0 || true
