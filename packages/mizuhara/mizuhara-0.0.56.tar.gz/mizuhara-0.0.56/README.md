THIS IS A DRAFT VERSION OF README.md

# Mizuhara

---

### Create Your Telegram Bot More Easily.(Draft)

---

#### I. Introduction

When you create a telegram bot with python, you may face with PyTelegramBotAPI or python-telegram-bot.
You may recognise that it is not easy to handler both two packages to create your own telegram bot.
These package are not a framework, so you have to design all structure from the scratch. 
You have to all functions to message or callback handlers as a minimum, 
additionally you may have to create another global variables to control telegram bot more precisely.
If you have any experience to write a code with python packages related with telegram, 
you might be frustrated that your code is so verbose and seems not to be able to be done maintenance.

This project, which is called Mizuhara(the origin of water), was started to solve the difficulties during producing telegram bot.
Mizuhara is mimic Django Rest API Framework(DRF), so you have to set the route, view as well as serializers.
Only difference between Mizuhara and Django is, the previous one does not provide any models, which are charge of defining table of database.
Mizuhara was created to be used with connecting REST-API server.

---

#### II. How to Use

##### 1. Prerequisite

* Python up to 3.11 version or equal.
* pip

##### 2. Installation

Install 'Mizuhara' by executing shell command below in your virtual environment.

```commandline
pip install mizuhara
```

After installation, you can use command 'mizuhara' on your shell terminal.

```commandline
mizuhara --help
```

##### 3. Create Project or App

Like Django, 'Mizuhara' requires to create project and app folder via command 'mizuhara'.
App, like a app in Django, is a smallest unit in your telegram bot project

```commandline
# create prject
mizuhara newproject

# create application in your project
mizuhara newapp <YOUR_APP_NAME>
```
You do not have to create your project first. 
If there is no project and you try to create an app, 'Mizuhara' will create file system for your project automatically.

##### 4. Write Your Code in Your Application Folder

Please refer to the documentation at the link below.

* Documentation Link: <a href="#"> Now_Preparing </a>


#### 4. Development Logs

* 2025.03.23 : Start demo test and debugging.
* 2025.03.22 : 1st debugging on PyPi. (current Pypi version is 0.0.18)
* 2025.03.18 : Convert filesystem for PyPi packaging.
* 2025.03.13 : Complete to create a draft version.
* 2025.02.07 : Start project 'telebot_framework'


THIS IS A DRAFT VERSION OF README.md
