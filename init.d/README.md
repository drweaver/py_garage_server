Create folder in /usr/local

```bash
sudo mkdir /usr/local/garagecontrol
```

Checkout the latest code

```bash
cd /usr/local/garagecontrol
sudo git clone https://github.com/drweaver/py_garage_server .
```

create file /usr/local/garagecontrol/smtp.pwd and add the password for your gmail account:

```bash
sudo nano /usr/local/garagecontrol/smtp.pwd
sudo chmod 400 /usr/local/garagecontrol/smtp.pwd
```

Ensure garage_config.json settings are correct for:
* logfile
* smtp_pwd_file
* authorised
* port

Create link to the init.d file

```bash
sudo ln -s /usr/local/garagecontrol/init.d/garagecontrol.sh /etc/init.d/garagecontrol
```

Test it is working

```bash
sudo /etc/init.d/garagecontrol start

tail -f /var/log/garage_service.log
```

Register it

```bash
sudo update-rc.d garagecontrol defaults
```

Once above is complete, use following commands to start and stop

```bash
sudo service garagecontrol start
sudo service garagecontrol stop
```
