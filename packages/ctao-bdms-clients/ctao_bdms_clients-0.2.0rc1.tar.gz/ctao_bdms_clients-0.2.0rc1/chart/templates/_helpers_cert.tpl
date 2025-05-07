{{- define "volume_mounts_rucio_config" }}
- name: rucio-config
  mountPath: /opt/rucio/etc/rucio.cfg
  subPath: rucio.cfg
- name: rucio-config
  mountPath: /opt/rucio/etc/alembic.ini
  subPath: alembic.ini
{{- end }}
{{- define "volume_mounts_cert" }}
- name: cafile
  subPath: ca.pem
  mountPath: /etc/grid-security/ca.pem
- name: dppsuser-certkey-400
  mountPath: /opt/rucio/etc/userkey.pem
  subPath: dppsuser.key.pem
- name: dppsuser-certkey-600
  mountPath: /opt/rucio/etc/usercert.pem
  subPath: dppsuser.pem
{{- end }}
{{- define "volumes_cert" }}
- name: rucio-config
  configMap:
    name: {{ template "bdms.fullname" . }}-rucio-config
- name: cafile
  secret:
    defaultMode: 420
    secretName: {{ template "certprefix" . }}-server-cafile
- name: dppsuser-certkey-600
  secret:
    defaultMode: 0600
    secretName: {{ template "certprefix" . }}-dppsuser-certkey
- name: dppsuser-certkey-400
  secret:
    defaultMode: 0400
    secretName: {{ template "certprefix" . }}-dppsuser-certkey
{{- end }}
{{- define "env_helm_release" }}
- name: HELM_RELEASE_NAME
  value: {{ .Release.Name }}
{{- end }}
