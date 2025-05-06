# Fire Starter User's Guide
#  Creating a new project utilizing uv

### OmniFocus
* Create a new project in OmniFocus Computing/Projects/<project>.
* Add any known non-standard task.

### Github
* Come up with a name for the project.
* Sign into github and go to the list of my repositories.
* Give the repository a name and optionally a description.
* Leave the repo as public.
* Don't create a readme.
* Use the MIT License.
* Hit the create button.


### Initial Setup
* Sign into my account on enki.
* Clone the github repository

```
cd /tmp
git clone github.com/jasmit35/<project>
```
* Run Cookie Cutter.

```
cd $HOME/devl
cookiecutter https://github.com/fpgmaas/cookiecutter-uv
```
* Replace the empty .git directory with the correct one.
```
mv /tmp/<project>.git .
```

### direnv



# Starting a new project


### Python setup
Install pyenv and the desired version of Python for the project.

`cd $HOME/devl/`*project_name*

`pyenv virtualenv 3.9.9 `*project_name*

`pyenv local `*project_name*

`pip-compile requirements.in >requirements.txt`

### Get the initial commit to Git completed
* Install the requirements.

`python -m pip install --requirement=requirements.txt`

* Move to the top level directory for the project.
* Get the initially generated code onto github.

`git init`

`git add .`

`git commit -m 'Initial Commit'`

`git remote add github https://github.com/jasmit35/`*project_name*`.git`

`git push -u github  master`


# Start of July 2024 update

## Test installation


###  Prepare code for testing

Commit all development changes:

```
git status
git add .
git commit -m "Changes for bugfix/v1.0.1"
git push github
```

###  Save any new docker images

Male sure the version number is set correctly in the Makefile.

Rebuild the image to make sure the version is tags correctly.

`make dbc-build`

Then push the image to Docker Hub for distribution.

`make push-image`

### Update Documentation

Update the defects and enhacemnts document to reflect what has been completed in this version.

### Install updated version on the test server (Enlil)

Signon to the appropriate target server using my normal ID.

**If FireStarter has not been updated to specify a release, stage the desired release in the /tmp directory before running auto_update. Then be sure to select the option to use the existing tar file.**

```
cd /tmp
git clone https://github.com/jasmit35/TROLoad.git --branch feature/v1.2.0
```

Archive the existing version:

```
cd ~/test/
tar -czvf TROLoad_2022_06_26.tar.gz TROLoad
mv TROLoad_*.tar.gz .archive
```

Clean up old archives

```
cd ~/test/.archives
ll
rm TROReports_2021*
```
Remove the existing version:

```
cd ~/test/
rm -rf TROReports
```
Use auto_update to install the code:

```
export ENVIRONMENT=test
auto-update -e test -a TROLoad
```

**If there are non-standard migration steps, handle them.**

### Update .db_secrets.env
The secrets files are not stored on GitHub because they contain user names and passwords. You need to manually copy the files:

```
cd /Users/jeff/prod/<app name>/local/etc
cp /Users/jeff/devl/TROReport/local/etc/.db_secrets.env .
```
### Set up Python:
```
pyenv versions
pyenv virtualenv 3.12.4 TROLoad
pyenv local TROLoad
```
### Install required packages:

```
cd ~/test/TROLoad/etc
pip install -r requirements.txt
```


## Production installation

###  Prepare code for release

Commit any remaining changes:

```
git status
git add .
git commit -m "Final changes for bugfix/v1.0.1"
git push github
```

Merge the changes into the master branch:

```
git status
git fetch
git checkout master
git pull github master
git merge bugfix/vX.X.X
git commit -m 'Commit of bugfix/vX.X.X into master'
git push github master
```
Create a new release branch:

```
git fetch
git branch
git checkout master
git branch release/vX.X.X
git checkout release/vX.X.X
```

Update the __init__.py file with the release number:

```
vi ~/devl/<app>/python/__init__.py
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
git branch
```

###  Save any new docker images

Male sure the version number is set correctly in the Makefile.

Rebuild the image to make sure the version is tags correctly.

`make dbc-build`

Then push the image to Docker Hub for distribution.

`make push-image`

### Update Documentation

Update the defects and enhacemnts document to reflect what has been completed in this version.

### Prepare the production server 

Archive the existing version:

```
cd ~/prod/
tar -czvf TROReports_2022_06_26.tar.gz TROReports
mv TROReports_*.tar.gz .archive
```

Clean up old archives

```
cd ~/prod/.archives
ll
rm TROReports_2021*
```
Remove the existing version:

```
cd ~/prod/
rm -rf TROReports
```

### Install on the production server 


Use auto-update to install the new release:

**If FireStarter has not been updated to specify a release, stage the desired release in the /tmp directory before running auto_update. Then be sure to select the option to use the existing tar file.**

```
cd /tmp
git clone https://github.com/jasmit35/TROReports.git --branch release/v0.0.0
```

```
export ENVIRONMENT=prod
auto-update -e prod -a TROReports
```
### Update .db_secrets.env
The secrets files are not stored on GitHub because the contain user names and passwords. You need to manually copy the files:

```
cd /home/jeff/prod/<app name>/local/etc
cp /Users/jeff/devl/TROReport/local/etc/.db_secrets.env .
```
### Set up Python:
```
pyenv versions
pyenv virtualenv 3.12.4 TROLoad
pyenv local TROLoad
```

### Install required packages:

```
cd /Users/jeff/prod/TROReports
pip install -r requirements.txt
```

### Perform application specific updates


# End of July 2024 update



## Bug fixes for an existing project
### Prepare the development environment

Make sure the code in the devl directories is up to date with the master branch in the repository.

```
cd ~/devl/<appname>
git status
```
If their are minor items such as documentation updates, go ahead and add them with their own commit so the master is up-to date locally and on git hub.

```
git add .
git commit -m "Final commit before next version."
git push github master
```
Revise the "Bugs and new features" document to reflect the current status. Update the version number for the fix or enhancement.

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

Update the __init__.py file with the release number:

```
vi ~/devl/<app>/local/python/__init__.py
git add .
git commit -m 'Updated init.py with the correct release number.'
```


Fix and test all the bugs listed in the document .../shared/Project Documentation/<app>/Bugs and New Features

Check the System Guide for the project to see if their are any non-standard step that won't be covered by Fire Starter. Perform only any that are necessary at this time. The rest will be reviewed again and performed latter.

Follow the project's documentation for testing a new release, but use the bugfix branch rather than the release branch. 

## Enhancements for an existing project

### Prepare the development environment

Make sure the code in the devl directories is up to date with the master branch in the repository.

```
cd ~/devl/<appname>
git status
```
If their are minor items such as documentation updates, go ahead and add them with their own commit so the master is up-to date locally and on git hub.

```
git add .
git commit -m "Final commit before next version."
git push github master
```
Use git to pull the existing code from the master branch on GitHub:

```
cd ~/devl/<app>
git fetch
git checkout master
git pull github master
git branch feature/vX.Y.Z
git push -u github feature/vX.Y.Z
git checkout feature/vX.Y.Z
```

Update the __init__.py file with the release number:

```
vi ~/devl/<app>/local/python/__init__.py
git add .
git commit -m 'Updated init.py with the correct release number.'
```
### Fix any current bugs

Revise the "Bugs and new features" document to reflect the current status. Update the version number for the fix or enhancement.

Fix and test all the bugs listed in the document .../shared/Project Documentation/<app>/Bugs and New Features

### Plan out the enhancement 

Check the System Guide for the project to see if their are any non-standard step that won't be covered by Fire Starter. Perform only any that are necessary at this time. The rest will be reviewed again and performed latter.

Follow the project's documentation for testing a new release, but use the bugfix branch rather than the release branch. 
### Complete the steps in Apendix A - ???













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


## Appendix A - Adding the Synology repository to an existing project

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



## Appendix B - Django projects

### OmniFocus
* Create a new project in OmniFocus Computing/Projects/*project_name*.
* Add any known task.


### Use cookie cutter to lay out the project:

`cd $HOME/devl/`

`cookiecutter gh:cookiecutter/cookiecutter-django`

### Create vitual environment pointing to desired version of Python:

`cd $HOME/devl/`*project_name*

`pyenv virtualenv 3.10.0 `*project_name*

`pyenv local ` *project_name*

### Install the requirements:

`cd $HOME/devl/`*project_name*

`pip install -r requirements/local.txt`

### Set up local git repository:

`cd $HOME/devl/` *project_name*

`git init`   # A git repo is required for pre-commit to install

`pre-commit install`

### Create a new PostgreSQL database using createdb:

`pgenv use 15.5`

`createdb --username=postgres <project_slug>`

### Create .env file to set environment variables:

`vi ~/devl/`*project_name*`/.env`

`export DATABASE_URL=postgres://postgres:<password>@127.0.0.1:5432/`*project_name*

### Commit what we have:

Have to commit twice. The first commit modifies files.

`git add .`

`git commit -m 'Inital commit'`

`git add .`

`git commit -m 'Inital commit'`



