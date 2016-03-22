import sync as sync
import json

with open('config.json') as c:
    config = json.load(c)

cloud = sync.getCloudDatabase(config["aws"]["user"], config["aws"]["password"], config["aws"]["host"], config["aws"]["port"])
local = sync.getLocalDatabase("eisvsfiles.db")
box = 8;


## IF SETTING UP THE FIRST TIME RUN THE FOLLOWING COMMANDS
#sync.createBlankLocalTable(local)
#sync.copyContentData(box, local, cloud)

## IF SYNCING AFTER RUNNING FIRST TIME SETUP RUN THE FOLLOWING COMMANDS
sync.syncBoxes(box, local, cloud)
