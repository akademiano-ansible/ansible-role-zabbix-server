egeneralov.zabbix-server
========================

Provision zabbix server installation.

Requirements
------------

- name: Debian
  versions:
    - wheezy
    - jessie
    - stretch
- name: Ubuntu
  versions:
    - trusty
    - xenial
    - zesty

Role Variables
--------------

Also see `defaults/main.yml`.

- **zbx_database**: `timescaledb`

- **zbx_server_conf**:
  - `{ "k": "", "v": "" }`

Dependencies
------------

- [egeneralov.zabbix_repository](https://github.com/egeneralov/zabbix-repository)
- [egeneralov.postgresql](https://github.com/egeneralov/postgresql)
- [egeneralov.timescaledb](https://github.com/egeneralov/timescaledb)

Example Playbook
----------------

    - hosts: zabbix-server
      vars:
        zbx_version: 4.2
      roles:
        - egeneralov.zabbix-server

License
-------

MIT

Author Information
------------------

Eduard Generalov <eduard@generalov.net>
