# Schedule Share
<img src=https://user-images.githubusercontent.com/31383711/204903829-ab7de929-6738-487e-8363-c3697b96a4e4.svg width=50 /> <img src=https://user-images.githubusercontent.com/31383711/190922610-d309b96e-318e-4e82-9b04-8eb2ab52938d.png width=50 />

___
This is an app that allows a a user to create events and invite trusted family 
and friends to participate in the event. The app will send an email, or text if 
signing up for that service, to invite them to participate.


## Setup
___

In order to run this app you will need to have Python installed with a virtual 
environment created and activated. If not sure how, you can find out 
[here](https://github.com/jalnor/install_documentation/blob/edd4efbefc403062b11f186d5d7ef8c9c27a2ad7/Python_Related/PYTHONINSTALL.md).

With the virtual environment activated, type:

``` pip install -r requirements.txt ```

into your terminal. Once the dependencies are installed you will need to instruct 
Django to create the database, type:

```
python manage.py makemigrations
python manage.py migrate
```
Now that the database is created, you can start the app with:

``` python manage.py runserver ```

You should now see the url displayed as hyperlink in terminal. 
Click to open browser.
