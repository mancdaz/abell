use admin;
db.createUser({
  user: "admin",
  pwd: "password",
  roles: [{
      role: "root",
      db: "admin"
    }, {
      role: "userAdminAnyDatabase",
      db: "admin"
    }
  ]
});
db.auth("admin","password");
use abell;
db.createUser({
  user: "abell",
  pwd: "123456",
  "roles": [
    {
      "role": "readWrite",
      "db": "abell"
    }
  ]
});
db.createCollection("assetinfo");
db.assetinfo.insert({"type":"server",
                     "managed_keys":['parent', 'children', 'asset_id'],
                     "unmanaged_keys":['patches'],
                     "system_keys":['owner','cloud','type','abell_id']})
db.createCollection("server");
db.server.createIndex({"abell_id":1}, {unique:true});
