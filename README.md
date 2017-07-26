Abell
===

[![Build Status](https://travis-ci.org/rcbops/abell.svg?branch=master)](https://github.com/rcbops/abell)

A distributed dynamic inventory system.

Installing with Docker
-------------
Install [Docker](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) and [Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-16-04).

cd into the top abell directory and run:

```
  $ sudo docker-compose build
  $ sudo docker-compose up -d
```
This will launch 2 containers and look something like this:

```
$ sudo docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                      NAMES
47cde2757ee8        abell_app           "/bin/sh -c 'pytho..."   52 seconds ago      Up 51 seconds                                  abell_app_1
d2794defee41        mongo:latest        "docker-entrypoint..."   53 seconds ago      Up 51 seconds       0.0.0.0:27017->27017/tcp   abell_db_1
```

Installing with RPC-O/OSA
-------------------------

For development purposes, it is possible to run Abell on an AIO. This can be done by following the Docker instructions above on the AIO host machine.

Abell will be started on localhost:5000, and will not intefere with the rest of the AIO. However, it is not currently integrated with or managed by RPC-O/OSA's playbooks.

Installing manually
-------------------

If you would like to run Abell manually, you must first prepare a local MongoDB database with an admin user.

Installing MongoDB is outside the scope of this document, however the user can be created with the `bootstrap_mongodb.sh` script.

Usage
---
In order to add an asset to abell, there must be an entry for that asset's "type". An asset type entry holds information on what fields each asset will contain, along with who has access to them. Here is an example server asset type:

```
{
    "type": "server"
    "system_keys": [
      "cloud",
      "abell_id",
      "owner",
      "type"
    ],
    "managed_keys": [
      "patches",
      "os",
      "cabinet"
    ],
    "unmanaged_keys": [
      "notes",
      "arbitrary_field1"
    ],

  }
```
System Keys are variables that must be provided during asset creation and are hard coded into abell, every asset and asset type in abell will have these keys. These fields are mainly for abell to logically map and track each asset, they cannot currently be changed.

Managed and Unmanaged keys are for the abell admin to define, and can be updated and deleted at any time. The idea is that managed keys are fields that don't often change and are only updated by very trustworthy sources, like the asset themselves or auditing automation. On the other hand, unmanaged keys are for the various users of abell who would like to store arbitrary key values specific to each asset. Things like notes or tags for external automation to key off of.

----------------------
#### Creating an asset type
Sending a dictionary with the following parameters will create an asset type  in abell.
###### Parameters:
```
{"type": "asset_type",
"managed_keys": ["Key1", "Key2", ...],
"unmanaged_keys": ["Key3", ...]}
```

###### Example:
```
curl -X POST http://<abell_ip:5000>/api/v1/asset_type \
  -H 'content-type: application/json' \
  -d '{"type": "server", "managed_keys": ["version", "patches"], "unmanaged_keys": ["notes"]}'
```

###### Returns:
```
{
  "code": 200,
  "details": {
    "info": "Asset type server created"
  },
  "payload": null
}
```
----------------------
#### Getting asset type info
This request will return all the fields for a given asset type.

###### Parameters:
```
type=asset_type
```

###### Example:
```
curl -X GET 'http://<abell_ip:5000>/api/v1/asset_type?type=server' \
  -H 'content-type: application/json'
```

###### Returns:
```
{
  "code": 200
  "payload": {
    "unmanaged_keys": [
      "notes"
    ],
    "managed_keys": [
      "version",
      "patches"
    ],
    "type": "server",
    "system_keys": [
      "abell_id",
      "owner",
      "cloud",
      "type"
    ]
  },
  "details": {}
}
```
----------------------
#### Updating asset type fields
This request will add, remove or swap fields for for an asset type.

**NOTE**: This command will be mirrored for every asset of the provided type i.e. removing a key from either managed or unmanaged will delete that field in **all assets** of that type. The same goes for adding a new field, all existing assets will have the new field with the value "None".

###### Parameters:
```
{"type": "asset_type",            # Required
"remove_keys": ["Key1"],          # Optional
"managed_keys": ["Key2"],         # Optional
"unmanaged_keys": ["new_key"]}    # Optional
```

###### Example:
This call will remove the "version" key from all assets of type server, add the key value pair "os": "None" to all server assets and swap notes and patches in the server asset type
```
curl -X PUT http://<abell_ip:5000>/api/v1/asset_type \
  -H 'content-type: application/json' \
  -d '{"type": "server","remove_keys": ["version"], "managed_keys": ["os", "notes], "unmanaged_keys": ["patches"]
}'
```

###### Returns:
```
{
  "code": 200,
  "payload": null,
  "details": {
    "new_keys": ["os"],
    "removed_keys": [
      "version"
    ],
    "info": "Asset server updated"
  }
}
```
----------------------
#### Delete asset type
This will remove an asset type from abell

**NOTE**: An asset type will only be removed if **ALL** assets of the given type are deleted from abell prior to this call.

###### Parameters:
```
type=asset_type
```

###### Example:
```
curl -X DELETE 'http://<abell_ip:5000>/api/v1/asset_type?type=server' \
  -H 'content-type: application/json'
```

###### Returns:
```
{
  "code": 200,
  "payload": null,
  "details": {
    "info": "Asset type server deleted"
  }
}
```
