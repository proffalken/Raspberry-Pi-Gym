# Pi Trainer

PiTrainer is a multi-functional personal trainer that lives in a Raspberry Pi Zero W.  This version counts skips via an accelerometer and
displays it on a Scroll phat HD as well as sending the count to a server.  It also accepts UDP messages to operate 3 mobile phone 
vibrators.  All the interfaces between threads and Client/Server use XML, making it simple to understand what is going on.  
Multi-threaded code to handle each of the tasks, communicating via Queue or socket. 

Related presentation to Raspberry Pint on 25 July 2017 can be found https://prezi.com/9dxeynmyy-eo/pi-trainer/

## Testing

To test PiTrainer, clone this repo and create a virtual environment as the *root* user on your pi (we
need root privileges for the SMBUS functionality):

```bash
pip install virtualenv
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
```

Now you can run the tests as follows:

```bash
python setup.py test
```

You should see the output of [Flake8](http://flake8.pycqa.org/en/latest/) linting scroll across your screen.
