#!/usr/bin/python

# Copyright: (c) 2019, Eduard Generalov <eduard@generalov.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': [
    'preview'
  ],
  'supported_by': 'community'
}


# DOCUMENTATION = '''
# ---
# module: zbx_user_manager
# 
# short_description: Zabbix user manager
# 
# version_added: "2.8.1"
# 
# description:
#   - "Module to manage zabbix users"
# 
# options:
#   name:
#     description:
#       - This is the message to send to the sample module
#     required: true
#   new:
#     description:
#       - Control to demo if the result of this module is changed or not
#     required: false
# 
# extends_documentation_fragment: []
# 
# author:
#   - Eduard Generalov <eduard@generalov.net>
# '''
# 
# 
# EXAMPLES = '''
# # Pass in a message
# - name: Test with a message
#   zbx_user_manager:
#     name: hello world
# 
# # pass in a message and have changed true
# - name: Test with a message and changed output
#   zbx_user_manager:
#     name: hello world
#     new: true
# 
# # fail the module
# - name: Test failure of the module
#   zbx_user_manager:
#     name: fail me
# '''
# 
# 
# RETURN = '''
# original_message:
#   description: The original name param that was passed in
#   type: str
#   returned: always
# message:
#   description: The output message that the sample module generates
#   type: str
#   returned: always
# '''




from ansible.module_utils.basic import AnsibleModule
from pyzabbix.api import ZabbixAPI, ZabbixAPIException
from time import sleep
import json


def is_credentials_valid(**kwargs):
  try:
    zapi = ZabbixAPI(**kwargs)
    sleep(0.1)
    if not zapi.user.logout():
      pass
    return True
  except ZabbixAPIException:
    return False


def get_userid_by_name(username, zapi):
  sleep(0.1)
  result = [
    i['userid']
    for i in zapi.do_request("user.get")["result"]
    if i['alias'] == username
  ][0]
  return result


def change_password(userid, new_passwd, zapi):
  sleep(0.1)
  result = zapi.do_request(
    "user.update",
    {
      "userid": userid,
      "passwd": new_passwd
    }
  )["result"]
  return result


def find_group_id_by_name(zapi, group_name):
  sleep(0.1)
  return [
    i['usrgrpid']
    for i in zapi.do_request("usergroup.get")['result']
    if i['name'] == group_name
  ][0]



def create_user(username, password, user_type, groups, zapi):
  sleep(0.1)
  try:
    r = zapi.do_request(
      "user.create",
      {
        "alias": username,
        "passwd": password,
        "usrgrps": [ { "usrgrpid": find_group_id_by_name(zapi, i) } for i in groups ],
        "type": user_type
      }
    )
    return True
  except ZabbixAPIException as e:
    return False



def update_user(username, password, user_type, groups, zapi):
  try:
    r = zapi.do_request(
      "user.update",
      {
        "userid": get_userid_by_name(username, zapi),
        "alias": username,
        "passwd": password,
        "usrgrps": [ { "usrgrpid": find_group_id_by_name(zapi, i) } for i in groups ],
        "type": user_type
      }
    )
    return True
  except ZabbixAPIException as e:
    return False


def main():
  
  changed = False
  
  module = AnsibleModule(
    supports_check_mode = False,
    argument_spec = {
      "url": {
        "type": "str",
        "required": True
      },
      "default_password": {
        "type": "str",
        "required": False,
        "default": "zabbix",
        "no_log": True
      },
      "login_password": {
        "type": "str",
        "required": True,
        "no_log": True
      },
      "users": {
        "type": "list",
        "required": False,
        "no_log": False
      }
    }
  )
  
  try:
    zapi = ZabbixAPI(**{
      'url': module.params['url'],
      'user': 'Admin',
      'password': module.params['default_password']
    })
    
    admin_userid = get_userid_by_name(
      username = 'Admin',
      zapi = zapi
    )
    
    change_password(
      userid = get_userid_by_name('Admin', zapi),
      new_passwd = module.params['login_password'],
      zapi = zapi
    )
    
    changed = True
    sleep(0.1)
    zapi.user.logout()
  except ZabbixAPIException as e:
    pass
  

  try:
    zapi = ZabbixAPI(**{
      'url': module.params['url'],
      'user': 'Admin',
      'password': module.params['login_password']
    })
    
    users_list = [
      i["alias"]
      for i in
      zapi.do_request("user.get")["result"]
    ]
    
    
    for user in module.params['users']:
      if user["name"] not in users_list:
        if not create_user(
          username = user['name'],
          password = user['password'],
          user_type = user['type'],
          groups = user["groups"],
          zapi = zapi
        ):
          return module.fail_json(
            msg = e.message,
            json = e.json
          )
        else:
          changed = True
          users_list = [
            i["alias"]
            for i in
            zapi.do_request("user.get")["result"]
          ]
          continue
      
      if not is_credentials_valid(**{
        'url': module.params['url'],
        'user': user['name'],
        'password': user['password']
      }):
        changed = True
        change_password(
          userid = get_userid_by_name(user['name'], zapi),
          new_passwd = user['password'],
          zapi = zapi
        )
        sleep(0.1)

      if not update_user(
        username = user['name'],
        password = user['password'],
        user_type = user['type'],
        groups = user["groups"],
        zapi = zapi
      ):
        return module.fail_json(
          msg = e.message,
          json = e.json
        )


    sleep(0.1)
    zapi.user.logout()
  except ZabbixAPIException as e:
    return module.fail_json(
      msg = e.message,
      json = e.json
    )

  result = {
    "changed": changed
  }

  module.exit_json(**result)


if __name__ == '__main__':
  main()

