# 1. Introduction

# 2. Prerequisites
- docker & docker-compose

OR

- make ```sudo apt install make```
- python3-dev python3-pip ```sudo apt install python3-dev python3-pip```
- Python >= 3.8

# 3. Document
- [Rasa](https://rasa.com/docs/rasa/installation)
- [Rasa X](https://rasa.com/docs/rasa-x/installation-and-setup/install/docker-compose)

# 4. Installation
## Option 1: Run with docker
```
    cp .env.example .env
    docker-compose up -d
```

Change folder permission
```
    sudo chgrp -R root ./*
    sudo chmod 777 -R models
    docker-compose stop
    docker-compose up -d
```

## Option 2: Install immediate to PC

- Install the requirements inside of a Python virtualenv (recommend)
```BASH
    pip install virtualenv
    virtualenv -p python3.8 venv
    source venv/bin/activate
```

- Make requirements
```BASH
    make requirements
```

- Start Rasa X
terminal 1 (http://localhost:5055)
```BASH
    rasa train
    rasa run actions
```

terminal 2 - UI (http://localhost:5005)
```BASH
    rasa x
```

Access link: [](http://localhost:5002)

# 5. Example rasa commands
(If use docker) Exec to docker
``
    docker exec -it lunch_rasa sh
    rasa train
    exit
``

- Train nlu and run in shell
```BASH
    rasa train nlu
    rasa shell nlu
```

- Stop
```BASH
    /stop
```

- Train all
```BASH
    rasa train
    rasa shell
    rasa run actions
    rasa x
```

- To deactivate
```
    deactivate
```

- To test connect to rasa server
```
    curl --request POST 'http://localhost:5005/webhooks/rest/webhook' \
    --data '{"sender":"Test","message":"hi"}'
```

# 6. Debug
```
    docker-compose logs
```

# 7. Test connect
```
sudo snap install ngrok
ngrok authtoken <key />
ngrok http 5005
```