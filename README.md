# Scrap Movies and TV Series Data

<!-- add badges from https://shields.io/badges -->

## Description
A python package that attempts to retrieve data related to Moving Pictures (movies and tv series) from the web. It uses selenium to do so and several website that are deemed useful by it's author.



## Installation Guide

### Local development  
An isolated environment on which we will install all the required packages.
Install the required packages before creating your virtual environment. 
```
sudo apt update
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12-dev python3.12-venv python3.12-tk
```
Create a folder within in which your venv will be created
``` 
mkdir ~/src/venvs
cd ~/src/venvs
```

### Create the virtual Environment 
The name of the virtual environment is completely up to you. 
My preferred name for this project is `venv_mpic`.  
```
python3.12 -m venv {name_of_your_virtual_environment}
```
Assuming that you named your virtual environment as `my_venv` (too abstract but will do for this guide) activate it by running:
```
source ~/src/venvs/my_venv/bin/activate
```

The last step needs to be repeated each time you open a new terminal window, and it can get be irritating to execute a lengthy command such as this one. So you can go ahead and create an alias on your `~/.bashrc` or `~/.zshcr` file. 

Install nano and use it to open your environment configuration file:
```
sudo apt install nano
nano ~/.zshrc
```
Add the alias for activating the project's venv in your configuration file:
```
alias mpic='source ~/src/venvs/my_venv/bin/activate'
```

### Install Packages

It's about time to get the source code for this branch and install the required packages for this project. 


Clone the [MovingPicturesFetcher](https://github.com/MovingPicturesPicker/MovingPicturesFetcher) in your `~/src/` folder. 

Go to the Repository activate your venv and install the packages.
```
cd ~/src/MovingPicturesFetcher
mpic
pip install -e . -r requirements.txt
```


## How to Run it
TBD

## Use Cases
TBD
