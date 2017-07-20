#!/bin/bash
mongo admin --host 127.0.0.1 --eval 'db.createUser({user:"admin", pwd:"password", roles: [{role:"userAdminAnyDatabase", db: "admin"}]});'
