# PROD WIKI
Old hardware becomes obsolete; old software goes into production every night. 

## Accessing prod
- From host server do `docker exec -it werecruit_prod /bin/bash` to login to werecruit container.

## First time installation checklist
* get a docker image based on ubuntu 20 LTS
* Python is installed ( 3.8 )
* git is installed
* postgres is installed ( 12 or above )
* run command `mkdir \etc\werecruit`
* run command `cd \etc\werecruit`
* run command `git clone <repo url> . `.
* run command `pip install -r requirements.txt` 
* create .env file & make sure all keys are configured

## starting weRecruit
* cd to `etc/werecruit` .
* Run `./werecruit_start.sh`
* if you get permission error please run `chmod +x werecruit_start.sh`. Typically file permissions are lost after you do git pull.

## stopping weRecruit
- cd to `/etc/werecruit`
- run `./wr_stop.sh`. This should stop gunicorn processes & also display the pid for scheduler python process.
- To stop weRecruit scheduler note down the pid listed in above step and run `kill <pid>`
- Confirm it is stopped by visiting werecruit website from browser & verify you get a gateway error.

## Maintenance checklist 
- if you want to stop and start werecruit, please follow the steps in [stop](#stopping-weRecruit) and [start](#starting-weRecruit) section respectively.

- Run `wr_maintain.sh` script to clean up *.log & *.out files 
- cleanup sessions related folder by ( TODO -> automate this step )
    - `cd /etc/werecruit/flask_session`
    - `rm *`
- DB backups ( Need to automate it)
    - currently backups are being taken by connecting to pg thru pg admin and taking back up on laptop. **Needs a better way**

- once in a while container may crash or stop , to restart do following from main contabo machine
    - run `docker ps -a` command to ensure werecruit_prod is listed.
    - run `docker start werecruit_prod` command to start the werecruit prod container

- Please note : To come out of werecruit_prod container without stopping it , please enter *ctrl+p followed by ctrl+q*. You will be taken back to the main contabo machine.
## Upgrade checklist ( TODO -> write script for this)
- from terminal login to the werecruit container. For creds contact admin.
- run  `cd /etc/werecruit` 
- [stop](#stopping-werecruit) werecruit  
    - run `git status` to list files you may changed on the prod.  
    - if the werecruit_start.sh is changed then you may first want to restore it on server b by running `git restore werecruit_start.sh`
- Db upgrade *if applicable*
- .env file update *if applicable*.
- *optionally* clean up flask sessions folder
- *optionally* clean up werecruit.log folder.
- run `git pull` to get all the latest code
- do `chmod +x werecruit_start.sh`. Note executable permisions are lost in every git pull which has a **modified version of wercecruit_start.sh**.
- run `we_recruit_start.sh`
- sanity test with test data 
    - test user acct -> rkanade@gmail.com

## How to create an docker image & move to another node - 
From the main contabo machine run following commands
- `docker pause werecruit_prod` ( this is our container name)
- `docker commit werecruit_prod werecruit_image`
- verify image is created by running `docker images` & ensure the new image is listed.
- `docker unpause werecruit_prod`.
- If you want to move the image created above from one machine (A) to another machine ( say B), run following commands
    - on machine A `docker save werecruit_image > werecruit_prod.tar`
    - copy the above tar file from A to B using scp from machine A to B.
    - on machine B, run `docker load --input werecruit_prod.tar`
    - on machine B, for **first time only** you need to run `docker run -dit -p 0.0.0.0:8280:5000/tcp --name werecruit_prod werecruit_image`. This will create and start the container.
    

