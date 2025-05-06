
# Installing FireStart on a new sever 

## Install pyenv

Use thier install script to download and install the software:

```bash
curl https://pyenv.run | bash
```

Add the following to my .bash_profile:

```bash
#  My stuff
export ENVIRONMENT=devl

#  pyenv - Tool for managing python environments
export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:$PATH
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
export PIP_REQUIRE_VIRTUALENV=true
```


## Download and build the desired version of Python:

Install the prerequisites needed by python:

```
sudo apt-get install build-essential python3-tk tk-dev  zlib1g-dev libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev libncurses-dev
```

```
pyenv install 3.12.4
pyenv versions
```

## Install FireStarter


Determine the current release of FireStarter. Clone the repository from GitHub.

```
cd /tmp
git clone https://github.com/jasmit35/FireStarter.git --branch master
```

Edit the .bashrc file to set an alias for 'auto_update':

```
#
alias auto-update="python3 ~/prod/FireStarter/local/python/auto_update.py"
```

Finish setting up the python virtual environment:

```
mkdir -p ~/prod/FireStarter
cd ~/prod/FireStarter
pyenv virtualenv 3.12.4 FireStarter
pyenv local FireStarter

```

Start trying to use auto-update to update FireStarter itself.

```
auto-update -e prod -a FireStarter
```



You will probably need to correct the following:


```
cd ~/prod/FireStarter
mkdir -p ~/prod/FireStarter/local/python
cd ~/prod/FireStarter/local/python
cp /tmp/FireStarter/local/python/auto_update.py .
```
Set up the shared modules:

```
mkdir -p ~/prod/local/python
cd ~/prod/local/python
scp jeff@enki:/Users/jeff/devl/local/python/run_shell_cmds.py .
cd ~/prod/FireStarter/local/python
ln -s ~/prod/local/python/run_shell_cmds.py .
```

Install requirements:

```
pip install config
python -m pip install --upgrade pip
```








## Starting a new project
### github
* Come up with a name for the project.
* Sign into github and go to the list of my repositories.
* Give the repository a name and optionally a description.
* Leave the repo as public.
* Don't use the options to create a readme, .gitignore or liscense.
* Hit the create button.

### OmniFocus
* Create a new project in OmniFocus Computing/Projects/*project_name*.
* Add the "Next set of enhancements" task.

### Initial Setup
* Review the Cookie Cutter Templates document to select the approrate template for the project.
* Sign into my account on Jobs.
* Move to the $HOME/devl directory.

`cd $HOME/devl`

* Run Cookie Cutter with the appropriate template.

`cookiecutter` *template_name*

### Python setup
Install pyenv and the desired version of Python for the project.

`cd $HOME/devl/`*project_name*

`pyenv virtualenv 3.8.2 `*project_name*

`pyenv local `*project_name*


### Get the initial commit to Git completed
* Install the requirements.

`python -m pip install --requirement=requirements.txt`

* Move to the top level directory for the project.
* Get the initially generated code onto github.

`git init`

`git add .`

`git commit -m 'Initial Commit'`

`git remote add origin https://github.com/jasmit35/`*project_name*`.git`

`git push -u origin master`



## Enhancing an existing project
Make sure the code in the devl directories  is up to date with the master branch in the repository.

`git status`

`git pull github master`

Create the new feature branch.

`git branch v0.2.0`

Check commits, tags and where HEAD is pointing.

`git log --oneline --decorate`

Switch to the new branch.

`git checkout v0.2.0`


### Finalizing the version in development

Check the System Guide for the project to see if their are any non-standard step that won't be covered by Fire Starter. Perform only any that are necessary at this time. The rest will be reviewed again and performed latter.

#### If you have been working on a Git branch, merge it with the master branch.

`git branch`

`git checkout master`

`git pull github master`

`git pull woz master`

`git merge`*branch*

`git push github master`

`git push woz master`

#### Update the defects and enhacemnts document to reflect what has been completed in this version.

#### Assign the new version number as a tag in Git.

Check the defects and enhancements document to make sure of the new application version number.

`git tag `*new application version*

`git push --tags github`

`git push --tags woz`

####  Save any new docker images

Male sure the version number is set correctly in the Makefile.

Rebuild the image to make sure the version is tages correctly.

`make dbc-build`

Then push the image to Docker Hub for distribution.

`make push-image`
  
## Test and Prod installation

Signon to the appropriate target server using my normal ID.

Use auto_update to install the code.

`auto_update -a `*project name*` -e ` *environment*

If there are non-standard migration steps, handle them.

## Bug Fixes
Use git to pull the existing code from the master branch on GitHub:

```
cd ~/devl/<app>
git fetch
git checkout master
git pull github master
git branch bugfix/vX.Y.Z
git push -u github bugfix/vX.Y.Z
git checkout bugfix/vX.Y.Z
```
Fix and test all the bugs listed in the document .../shared/Project Documentation/<app>/Bugs and New Features

Commit all changed code:

```
git status
git add .
git commit -m "Changes for bugfix/v1.0.1"
git push github
```

Follow the project's documentation for testing a new release, but use the bugfix branch rather than the release branch. 

Once all testing is successful, merge the changes into the master branch.

```
git status
git fetch
git checkout master
git pull github master
git merge bugfix/vX.X.X
git commit -m 'Commit of bugfix/vX.X.X into master'
git push github master
```
Once all desired bug fixes and new features have been completed, create a new release branch (see below).

## New Features
Use git to create a new feature branch (local and on GitHub) then move to it.

```
git fetch
git checkout master
git pull github master
git branch feature/vX.X.X
git push -u github feature/vX.X.X
git checkout feature/vX.X.X
```

Code and test the new feature.


Make sure all changes are in:

```
git add .
git commit -m 'Final commit before migration to test.'
```
Merge the new feature into the master branch:

```
git checkout master
git merge feature/vX.Y+1.0
git commit -m 'Commit of feature vX.Y+1.0 into master.'
git push github master
```

## New Releases

Create a new local branch and switch to it:

```
git fetch
git checkout master
git branch release/vX.X.X
git checkout release/vX.X.X
```

Update the __init__.py file with the release number:

```
vi ~/devl/<app>/local/python/__init__.py
git add .
git commit -m 'Updated init.py with the correct release number.'
```

Create a new branch on GitHub based on the new local branch:

```
git push -u github release/vX.X.X
```

Switch back to the local master branch so no changes are made to the release:

```
git checkout master
```

## Upgrading to a new release (temporary step)

Clone the code (to test or prod):

```
cd /tmp
git clone https://github.com/jasmit35/<app>.git --branch release/vX.X.X
```

## Appendix A - Adding a WOZ git repository to a project

`git remote -v`

`git remote rename origin github`

`git remote add woz git@woz.local:/opt/app/git/`*project_name`.git`

## Appendix B - Adding the Synology repository to an existing project

### Create the "new" repository

Sign on to the Synology server:

`ssh -p 2222 synology.local`

Set up a new directory for the project:

```
cd /volume1/GITRepo
mkdir TROLoad
chmod 750 TROLoad
cd TROLoad
git init --bare
```
 
### Add the repository to the project

`git remote add synology ssh://jeff@synology.local:2222/volume1/GITRepo/<Project>.git`



## Appendix C - Setup to support bare metal server

Start by setting up the Python virtual environment support:

```
cd
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
```

```
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

```
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
```

Download and build the desired version of Python:

```
pyenv install 3.9.9
pyenv global 3.9.9
pyenv versions
```

#########


Determine the current release of FireStarter. Clone the repository from GitHub.

```
cd /tmp
git clone https://github.com/jasmit35/FireStarter.git --branch master
```

Edit the .bashrc file to set an alias for 'auto_update':

```
#
alias auto-update="python3 /Users/Jeff/prod/FireStarter/local/python/auto_update.py"
```

Finish setting up the python virtual environment:

```
cd /home/jeff/prod/FireStarter
pyenv virtualenv 3.9.9 FireStarter
pyenv local FireStarter

```

Start trying to use auto-update to update FireStarter itself. You will probably need to correct the following:

```
mkdir -p ~/prod/FireStarter
cd ~/prod/FireStarter

mkdir -p ~/prod/FireStarter/local/python
cd ~/prod/FireStarter/local/python
cp /tmp/FireStarter/local/python/auto_update.py .
```
Set up the shared modules:

```
mkdir -p ~/prod/local/python
cd ~/prod/local/python
scp jeff@192.168.4.41:/Users/jeff/prod/local/python/run_shell_cmds.py .
cd ~/prod/FireStarter/local/python
ln -s /home/jeff/prod/local/python/run_shell_cmds.py .
```
