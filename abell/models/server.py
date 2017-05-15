# import cerberus
# from asset import AbellAsset
#
# NEW_SERVER_SCHEMA = {
#         'owner': None,
#         'cloud': None,
#         'server_id': None,
#         'account': None,
#         'name': None,
#         'type': 'server',
#         'core_status': None,
#         'core_name': None,
#         'role': None,
#         'tags': None,
#         'os': None,
#         'parent': None,
#         'children': None
# }
# # CREATE_SERVER_SCHEMA = {'owner': {'type': 'string'},
# #                         'cloud': {'type': 'string'},
# #                         'asset_id': {'type': 'string'},
# #                         'server_id': {'type': 'string'},
# #
# #
# #                     'account': {'type': 'string'},
# #                  'primary_ip': {'type': 'string'},
# #                  'compute_in_novadb': {'type': 'string'},
# #                  'boot_status': {'type': 'string'},
# #                  'boot_os': {'type': 'string'},
# #                  'number': {'type': 'string'},
# #                  'hardware': {'type': 'string'},
# #                  'terraform': {'type': 'string'},
# #                  'xs_release': {'type': 'string'},
# #                  'data_center': {'type': 'string'},
# #                  'needs_reboot': {'type': 'string'},
# #                  'server_id': {'type': 'string'},
# #                  'name': {'type': 'string'},
# #                  'type': {'type': 'string', 'allowed': ['server']},
# #                  'region': {'type': 'string'},
# #                  'core_status': {'type': 'string'},
# #                  'core_name': {'type': 'string'},
# #                  'cell': {'type': 'string'},
# #                  'date_online': {'type': 'string', 'nullable': True},
# #                  'role': {'type': 'string'},
# #                  'dns': {'type': 'string'},
# #                  'os': {'type': 'string'},
# #                  }
#
#
# class Server(AbellAsset):
#     def __init__(self, abell_id, property_dict=None):
#         AbellAsset.__init__(self, 'server', abell_id)
#         if property_dict:
#             self.add_property_dict(property_dict)
#
#     def validate(self):
#         v = cerberus.Validator(SERVER_SCHEMA)
#         v.allow_unknown = True
#         v.validate(self.__dict__)
#         return v
