# Sentinel notebooks and MSTICPy outside AML

This article describes how to set up and use Jupyter notebooks with
Microsoft Sentinel outside the default Azure Machine Learning (AML) environment.

We will describe the choices you have for both a notebook client and for creating your Jupyter environment.
Then we'll describe how to retrieve and configure the correct settings for Microsoft Sentinel.

# Contents
- Choosing a notebook environment
- Choosing a notebook client
- Building a local Jupyter environment
  - Installing Python and Jupyter
  - Installing Anaconda
  - Install Jupyter Lab
  - Test Jupyter Lab
  - Create a Jupyter kernel
- Building a Jupyter Docker environment
  - Docker requirements
  - Create the Dockerfile
  - Build the docker image
  - Running the docker image
  - Mounting a local folder
- Installing the MSTICPy package
- Getting the Sentinel Notebooks into your environment
- Configuring MSTICPy
  - Microsoft Sentinel
  - Test Sentinel Data Query
  - Threat Intelligence Providers
  - GeoIP Providers



## Choosing a notebook environment

There are three main options and a few other (untested) options

- Local Jupyter  install - this involves installing and running Python and Jupyter on your local machine
- Docker - this is still a local option but the Python and Juptyer code are pre-configured and run in a container.
- Remote Jupyter hub - this is more appropriate for shared notebook working. With this option you install Jupyter Hub on a host or virtual machine then access it locally using one of the Jupyter clients.

Other options that you may want to consider and test are using another notebook provider such as Google CoLab or Amazon Sagemaker. We have not tested the use of MSTICPy or notebooks accessing MS Sentinel in these environments though.

## Choosing a notebook client
There are several options available here.

- Jupyter classic - this is the original Jupyter client and, although no longer officially supported by the Jupyter team, is still in widespread use and has a lot of community support.
- Jupyter lab is the evolution of Jupyter and has more advanced and user-friendly interface (such as multi-tabbed notebooks, variable explorer) as well as having a more solid and more secure extension framework than  Jupyter classic.
- Visual Studio code - has a great notebook experience with similar capabilities to Jupyter lab.
- PyCharm, another code editing environment also has good notebook support

All of these clients have a rich ecosystem of extensions that can add capabilities
such as code formatting, spell checking, code snippets, version control and code
debugging.

One minor downside with both VSCode and PyCharm is that they are primarily aimed at developers, so the look and feel may be a little intimidating at first for non-developers.
However, they also bring capabilities such as advance debugging, object/variable
inspect as well more capabilities for developing related code such as Python
libraries.

The notebook clients listed above are not specific to any notebook
environment and you can freely switch between them. Some notebook enviroments such
as Azure ML, Azure Data Explorer, Google CoLab and Amazon Sagemaker also have
their own notebook clients that may bring additional features.




## Building a local Jupyter environment

There are two main options here
- you can install Python and Jupyter manually
- you can install the Anaconda distribution - this contains Python
  and many popular data analysis packages that you will be using.

The main advantage of the Anaconda (or Conda) installation is that it
has tighter package management than native Python, so you are less likely
to run into version conflict problems. There is however an overhead - things
take longer to install. We recommend using Anaconda but, once you have
your environment set up there is very little day-to-day difference.


### Installing Anaconda

Anaconda is popularly referred to as "Conda" - we will use that
term from now on in this document.

You can download the conda installer from https://www.anaconda.com/products/distribution

Follow the instructions on the site and from the installer.

The installation creates an application icon to start a conda terminal
or command prompt (this is usually the easiest way to get to your
Conda/Python installation on Windows - on Linux or Mac you should just
be able to open a new terminal and type the `conda` command directly).

#### Creating a Conda virtual environment

```bash
> conda create --yes --name conda-jupyter
Collecting package metadata (current_repodata.json): done
Solving environment: done

## Package Plan ##

  environment location: F:\anaconda\envs\conda-jupyter

Preparing transaction: done
Verifying transaction: done
Executing transaction: done
#
# To activate this environment, use
#
#     $ conda activate conda-jupyter
#
# To deactivate an active environment, use
#
#     $ conda deactivate
```
At
Activate the environment as follows
```bash
> conda activate conda-jupyter
```
You should notice that your prompt is now
prefixed with the environment name.

Now, when you run `python` (or `python3`), it will execute the instance
of Python belonging to that Conda environment.

To deactivate the environment (and return to using the system Python)
```bash
> conda deactivate
```

To delete a Conda environment, deactivate it and then execute.

```bash
> conda remove -n conda-jupyter --all
```

### Installing Python and Jupyter

Most Linux distributions come with a relatively modern version of Python 3. Mac and Windows do not have Python 3.x installed. On Windows running the command `python` will trigger an install of the latest Python version from the store. Alternatively, for both of these
platforms you can use the official Python installer for your system at https://www.python.org/downloads.

See this article on RealPython for details of Python installation on Linux, Windows and Mac
https://realpython.com/installing-python/


#### Creating a Python virtual environment

Python virtual environments are a type of installation sandbox. They have
two main benefits:
- You can install packages without affecting your base Python installation (useful
  if you mess things up)
- You can have several virtual enviroments with different versions to support
  different applications.

We would always recommend creating a virtual environment for your notebook work.

There are a number of Python virtual environment options but the simplest to
get going with is the built in `venv`.

In the following example we're creating an environment named `py-jupyter` and then
activating it.
You may want to have a folder to
contain all of your virtual environment folders or you may want to keep the virtual
environment in the same folder structure as your notebooks. Replace
`<path-to-envs>` with the folder of your choice.

**Linux/Mac**
```bash
> cd <path-to-envs>
> python3 -m venv py-jupyter
. py-jupyter/bin/activate
```
**Windows**
```bash
> cd <path-to-envs>
> python -m venv py-jupyter
> ./py-jupyter/scripts/activate
```
You should notice that your prompt is now
prefixed with the environment name.

Now, when you run `python` (or `python3`), it will execute the instance
of Python belongin to that environment.

To deactivate the environment (and return to using the system Python)
```bash
> deactivate
```

To delete a virtual environment, deactivate it and then simply delete
the environment folder.



### Install Jupyter Lab

Even if you are not intending to use Jupyter Lab as your client, it is
a good idea to have this as back up. Installing Jupyter Lab will ensure
that all of the required Jupyter Python dependencies are installed so that
you can use with any client.

This command installs quite a few packages so will take a minute or two to
complete.

#### In native Python
```bash
> pip install jupyterlab
Collecting jupyterlab
  Downloading jupyterlab-3.4.2-py3-none-any.whl (8.8 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.8/8.8 MB 43.1 MB/s eta 0:00:00
Collecting ipython
  Downloading ipython-8.3.0-py3-none-any.whl (750 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 750.8/750.8 KB 23.9 MB/s eta 0:00:00
Collecting jupyter-core
  Downloading jupyter_core-4.10.0-py3-none-any.whl (87 kB)
...
  Running setup.py install for json5 ... done
Successfully installed MarkupSafe-2.1.1 Send2Trash-1.8.0 anyio-3.6.1 argon2-cffi-21.3.0 argon2-cffi-bindings-21.2.0 asttokens-2.0.5 attrs-21.4.0 babel-2.10.1 backcall-0.2.0 beautifulsoup4-4.11.1 bleach-5.0.0 certifi-2022.5.18.1 cffi-1.15.0 charset-normalizer-2.0.12 colorama-0.4.4 debugpy-1.6.0 decorator-5.1.1 defusedxml-0.7.1 entrypoints-0.4
...
traitlets-5.2.1.post0 urllib3-1.26.9 wcwidth-0.2.5 webencodings-0.5.1 websocket-client-1.3.2 zipp-3.8.0
```

#### In Conda
```bash
> conda install --yes jupyterlab
Collecting package metadata (current_repodata.json): done
Solving environment: done

## Package Plan ##

  environment location: F:\anaconda\envs\conda-jupyter
...
pyrsistent-0.18.0    | 87 KB     | ########################################################################################################## | 100%
zlib-1.2.12          | 116 KB    | ########################################################################################################## | 100%
jsonschema-4.4.0     | 140 KB    | ########################################################################################################## | 100%
Preparing transaction: done
Verifying transaction: done
Executing transaction: done
```

### Test that Jupyter lab is working

```bash
> jupyter lab
[I 2022-05-23 19:02:46.329 ServerApp] jupyterlab | extension was successfully linked.
[I 2022-05-23 19:02:46.347 ServerApp] nbclassic | extension was successfully linked.
....
[I 2022-05-23 19:02:48.984 ServerApp] Serving notebooks from local directory: e:\pyenvs
[I 2022-05-23 19:02:48.984 ServerApp] Jupyter Server 1.17.0 is running at:
[I 2022-05-23 19:02:48.984 ServerApp] http://localhost:8888/lab?token=e679fdcc4c665f0541bc219fb9e1531a1ea8e778321af47a
[I 2022-05-23 19:02:48.984 ServerApp]  or http://127.0.0.1:8888/lab?token=e679fdcc4c665f0541bc219fb9e1531a1ea8e778321af47a
[I 2022-05-23 19:02:48.984 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 2022-05-23 19:02:49.137 ServerApp]

    To access the server, open this file in a browser:
        file:///C:/Users/Ian/AppData/Roaming/jupyter/runtime/jpserver-56612-open.html
    Or copy and paste one of these URLs:
        http://localhost:8888/lab?token=e679fdcc4c665f0541bc219fb9e1531a1ea8e778321af47a
     or http://127.0.0.1:8888/lab?token=e679fdcc4c665f0541bc219fb9e1531a1ea8e778321af47a
```

This should open Jupyter lab in your browser.
If it does not, copy and paste one of the URLs shown in the output into
your browser address bar.

### Jupyter working folder

When you start Jupyter, it uses the current working directory
as the root of its file system. It is not possible to browse for files
outside of this folder. You should typically start the Jupyter service
from the folder containing the notebooks that you want to use and
save.

### Creating a Jupyter (IPython) kernel

Although we have created a virtual environment in which we can install our
packages, we need to tell Jupyter about this environment using `ipkernel`
so that we can select and use it when we're running a notebook.

If are not using Conda, you need to install this using for the following command.
`ipykernel` is installed with the jupyterlab Conda package.

```bash
> pip install ipykernel
...
```

Run ipykernel to create the Jupyter kernel based on the current Python/Conda environment.
Ensure that the Python environment you created earlier is activated before running this command.

```bash
> python -m ipykernel install --user --name py-jupyter-sentinel --display-name "Python Sentinel"
```

#### Check that the kernel is visible in Jupyter

If your Jupyter lab instance is still running, kill it by typing `Ctrl-C`/`Cmd-C`
at the terminal.

Restart Jupyter - `jupyter lab`.

You should now see options to create a new notebook with the
kernel that we just created in addition to the default Python3 kernel.

![Notebook kernels](/e/src/blogs/sentinel-no-AML/notebook_kernels.png)

## Building a Jupyter Docker environment

### Docker requirements

You need to have Docker runtime or Docker desktop installed on the
system to execute these commands.

### Create Dockerfile

Create a text file with the following content and save it.
This used one of the Jupyter docker images as a base and then installs
MSTICPy into the Python environment.

In the subsequent command we're assuming that you name this file 'Dockerfile'

```dockerfile
# See here for image contents: https://hub.docker.com/r/jupyter/scipy-notebook
FROM jupyter/datascience-notebook

# installing Msticpy requirements and dependencies
RUN pip install --upgrade msticpy[all]
```

### Build the Docker image
This command will build your dockerfile into a docker image.

```bash
> docker build --pull -f "Dockerfile" -t msticpy:notebooks "."
```

### Running the docker image

This starts the image in a container.
We use the `-p` parameter to tell Docker to expose the container port 8888
(which is what Jupyter lab is listening on) as port 10000 on our local machine.

```bash
> docker run -p 10000:8888 msticpy:notebooks
```

This should produce console output from starting Jupyter Lab
```
Entered start.sh with args: jupyter lab
Executing the command: jupyter lab
[I 2022-05-24 21:53:16.198 ServerApp] jupyterlab | extension was successfully linked.
[W 2022-05-24 21:53:16.205 NotebookApp] 'ip' has moved from NotebookApp to ServerApp. This config will be passed to ServerApp. Be sure to update your config before our next release.
...

[C 2022-05-24 21:53:16.422 ServerApp]

    To access the server, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/jpserver-7-open.html
    Or copy and paste one of these URLs:
        http://7f0dc8699bf6:8888/lab?token=cd360b2a982a58490adfb679919fd4360bd6f0c4eb9f14ca
     or http://127.0.0.1:8888/lab?token=cd360b2a982a58490adfb679919fd4360bd6f0c4eb9f14ca

```

Copy the last of these URLs (the http://127.0.0.1... URL) and paste into
your browser address bar. Before hitting `Enter` edit the URL to change the port
number from 8888 to 10000.

It should look something like this:
```
http://127.0.0.1:10000/lab?token=cd360b2a982a58490adfb679919fd4360bd6f0c4eb9f14ca
```
Note: the token UUID is different on every invocation of Jupyter, so will be
different in your installation.

Stop the Docker container

First find the container ID of your running image
```bash
> docker ps
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS                    PORTS                     NAMES
7f0dc8699bf6   msticpy:notebooks "tini -g -- start-no…"   18 minutes ago   Up 18 minutes (healthy)   0.0.0.0:10000->8888/tcp   hopeful_franklin
```

And use docker stop to stop the container
```bash
> docker stop 7f0dc8699bf6
7f0dc8699bf6
```

### Mounting a local folder
Because docker containers do not persist data we want to specify
a location where we can save our notebooks to. You can do this
in one of two ways:

- mount a local filesystem folder
- create a docker volume

Creating and using a docker volume is the preferred way of managing
stateful data (since it gives limited access to the host filesystem
from the docker containers). You would want to do this if you were creating
a shared docker host for multiple users.

For local docker installations it is simpler to mount a host folder
into the container. We can do this with the `-v` switch to `docker run`

```bash
> docker run -p 10000:8888 msticpy:notebooks -v e:/src/notebooks:/notebooks -w /notebooks
```
Here we are mounting the local folder `e:/src/notebooks` from the
container to the local mount point `/notebooks`. That is, the contents
of our hosts folder `e:/src/notebooks` will readable and writeable
as /notebooks by the Jupyter process running in the container.

We've also used the `-w` parameter to tell the container process to
use `/notebooks` as the current working directory, so this will appear
as the root folder for our Jupyter lab.

Copy the URL as before and paste into the browser (remembering to modify the port number)
to start using Jupyter.

Note: we are not creating a Python virtual environment here since the
docker image is itself a kind of virtual environment that does not
persist changes and that we can easily rebuild.


## Building a shared Jupyter Hub

Setting up a shared Virtual machine or shared host for Jupyter hub
is beyond the scope of this article. However, there are some
easy to use options available. One of these is the Azure Data Science
Virtual Machine (DSVM) which comes pre-configured with Anaconda
and Jupyter Hub. Amazon, Google and other cloud providers have
similar offerings.

Documentation for JupyterHub is available here https://jupyterhub.readthedocs.io/

Here is a quick overview of the process as it applies to the Azure DSVM:

- Create your DSVM - choose Ubuntu (20.02 LTS recommended), since the Windows DSVM does
  not include JuptyerHub - https://docs.microsoft.com/azure/machine-learning/data-science-virtual-machine/dsvm-ubuntu-intro
- (Optionally but recommended) Add the DSVM to Azure Active Directory to enable domain-managed accounts - https://docs.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/dsvm-common-identity
  See also the JupyterHub documentation about JuptyerHub support for OAuth https://jupyterhub.readthedocs.io/en/stable/getting-started/authenticators-users-basics.html#use-oauthenticator-to-support-oauth-with-popular-service-providers
- Grant Azure permissions for your users to log in to the DSVM
- Ensure network filtering rules allow access to the JupyterHub port (usually 443 - see network
  configuration guidance in JupyterHub documentation - https://jupyterhub.readthedocs.io/en/stable/getting-started/networking-basics.html)
- (Optionally) configure and mount shared storage



## Installing the MSTICPy package

Many of our Microsoft Sentinel notebooks depend on MSTICPy.
It is a cybertools Python library that abstracts a lot of common
tasks that would otherwise have to be written in or pasted into
each notebook.

To read more about MSTICPy see the documentation site https://msticpy.readthedocs.io/

If you opted for the Docker installation, you will have already installed
msticpy so you can skip the rest of this section.

If you installed Python and Jupyter (either native Python or from Conda)
you will need to install MSTICPy.

Create a new notebook and select the `py-jupyter` or `conda-jupyter` kernel
that we created earlier. Create a new notebook cell enter and run the following:
```python
%pip install --upgrade msticpy[all]
```

Note: specifying the `[all]` qualifier tells `pip` to install all of the
optional dependencies for MSTICPy. You can choose to omit this but may
find that some features of MSTICPy will not work - you will typically
see a Python import error or a MissingExtra MSTICPy error.

You can also install msticpy from the command line but be sure to
activate the Python or Conda environment before installing.

## Importing and initializing MSTICPy

In order to use any of the MSTICPy features in a notebook
you need to import it a notebook cell.

```python
> import msticpy
```

Importing MSTICPy does the following things:
- Reads in settings from msticpyconfig.yaml
- Imports some of the core MSTICPy functionality such as Pivot functions
  and DataFrame accessors - a lot of MSTICPy functionality is
  available via a Pivot function or as a pandas DataFrame extension
  method.
- Imports some utility functionality such as:
  - msticpy.check_version() - to check the currently installed version against the latest published
  - 
### Initialization

MSTICPy has many hundreds of classes, functions and modules so no
single import statement will <\<TBD\>>


## Configuring MSTICPy

MSTICPy uses a configuration file `msticpyconfig.yaml` to
hold details about services that you want to access from the
notebooks.

Among these are:

- Microsoft Sentinel - the identifying information for each Sentinel Workspace that you want to use
- Threat Intelligence Providers - services such as VirusTotal, RiskIQ, AlienVault OTX and
  others need connection information and usually an API key for your account.
- Data Providers - other providers such as Splunk, MS Defender have their configuration here.
- Azure - you configure the authentication options you want to use for Azure as well as
  the Azure cloud you are using (if not the Azure global cloud)
- GeoIP providers - access keys to use IP to geolocation services


We will set up some basic configuration in this section.
More detailed information is available in the MSTICPy docs at
https://msticpy.readthedocs.io/GettingStarted.html.



### Microsoft Sentinel

Each MS Sentinel workspace needs the following information:

- Workspace Name
- Workspace ID
- Tenant ID (see note below)
- Subscription ID
- Resource Group

Note: the Tenant ID should be the tenant ID of the account
that you are using. This might not be the same as the tenant ID
of the workspace. This is not common but is the case if you
are using delegation to access the workspace, using Azure Lighthouse.

The easiest place to find most of this information is in the
Azure portal for your MS Sentinel workspace.
1. Browse to your workspace in the Azure management portal.
   (https://ms.portal.azure.com/ for Azure global cloud)
2. Select **Microsoft Sentinel** service and choose your workspace.
3. Select **Settings** (from the menu on the left of the screen)
4. Select **Workspace Settings**

<<IMG>>

You should see your the details for Workspace name and ID, subscription
ID and Resource Group.

To obtain your Tenant ID you can use a tool from MSTICPy - this
will retrieve the Tenant ID to which the workspace belongs.
If you are using delegated authentication via Azure Lighthouse
you will need to find your Tenant ID from your administrator
or by browsing to your account properties
(https://ms.portal.azure.com/#settings/directory) in the Azure portal.




```python
# Get the workspace tenant ID
from msticpy.config.ce_common import get_def_tenant_id
get_def_tenant_id("3c1bb38c-82e3-4f8d-a115-a7110ba70d05")
```

### Add the workspace details to settings

Import msticpy and run `msticpy.MpConfigEdit()` in a notebook
cell as shown below

1. Ensure that you have the Microsoft Sentinel tab selected
   and click on the **Add** button.

2. Copy the workspace details that you obtained in the previous
   step and paste them into the corresponding fields.
3. The **Name** field can be same as the workspace name or more friendly
   string - you can use this to reference the settings for
   this workspace.

Note: If you are using MSTICPy 2.0 or later there are a couple of
shortcuts available
- You can paste the Sentinel portal URL into the **Portal URL**
  text box and import the settings from this.
- You can paste the Workspace ID into the Workspace ID field
  and click on the **Resolve** button.

For both of these options you will need to authenticate to
Azure. A reliable way to do this is to login with the Azure CLI
before running the configuration tool:

```
!az login
```

4. Click the **Update** button to add the changes to the settings
5. If this is your main or only workspace you can also click on
   the **Set as default** button. This creates a copy of the current
   workspace settings and gives it the friendly name "Default".
   This lets you connect to this workspace without having to
   specify a a workspace name.
6. Click the **Save Setting** button to save the settings to
   the configuration file.

You can specify a different path in the **Conf File** text box or
continue to save settings to the file created in the current
directory and move it later.



```python
import os
os.environ["MSTICPYCONFIG"] = ""
```


```python
import msticpy
msticpy.MpConfigEdit()
```

# TODO
Need to include a ref to 

- conda install PyGObject libsecret

for Linux envs 

# Getting Sentinel Notebooks into your Environment

# ------TODO ---------

git or zip download

## Setting an Environment variable to reference msticpconfig.yaml

MSTICPy uses the following order for finding a msticpyconfig.yaml to use.

- TBD

Configuring msticpyconfig.yaml in different environments:

- Local Jupyter
- Docker
- Cloud notebooks

## Take next sections from Getting Started notebook



# <<\<TBD - ignore the following sections\>>>

**Note -  - this is taken**
**from existing guidance - we would link to this rather**
**than repeat it here**

---

---

# 2. Initializing the notebook and MSTICPy

<details>
  <summary>What are Python packages?</summary>
To avoid having to type (or paste) a lot of complex and repetitive code into
notebook cells, most notebooks rely on third party libraries (known in the Python
world as "packages").

Before you can use a package in your notebook, you need to do two things:

- install the package (although the Azure ML Compute has most common packages pre-installed)
- import the package (or some part of the package - usually a module/file, a function or a class)
</details>

## MSTICPy

**MSTICPy** (pronounced miss-tick-pie) is a Python package of CyberSecurity tools for data retrieval, analysis, enrichment and visualization.

## Initializing notebooks

At the start of most Microsoft Sentinel notebooks you will see an initialization cell like the one below.
This cell is specific to the MSTICPy initialization:

- it defines the minimum versions for Python and MSTICPy needed for this notebook
- it then imports and runs the `init_notebook` function.

<details>
    <summary>More about <i>init_notebook</i>...</summary>
    <p>
`init_notebook` does some of the tedious work of importing other packages,
checking configuration (we'll get to configuration in a moment) and, optionally,
installing other required packages.</p>
</details>
<br>

<div style="border: solid; padding: 5pt">
<b>Notes: </b>
<p>1. Don't be alarmed if you see configuration warnings (such as "Missing msticpyconfig.yaml").<br>
We haven't configured anything yet, so this is expected.</p>
<p>2. You may also see some warnings about package version conflicts. It is usually safe
to ignore these.</p>
</div>

The `%pip install` line ensures that the latest version of msticpy is installed.


```python
# import some modules needed in this cell
from IPython.display import display, HTML

display(HTML("Checking upgrade to latest msticpy version"))
%pip install --upgrade --quiet msticpy[azuresentinel]


REQ_PYTHON_VER="3.8"
REQ_MSTICPY_VER="1.5.2"

# initialize msticpy
import msticpy
msticpy.init_notebook(namespace=globals());
```

---

# 3. Querying Data from Microsoft Sentinel

Once we've done this basic initialization step,
we need to make sure we have configuration to tell MSTICPy how to connect
to your workspace.

This configuration is stored in a configuration file (`msticpyconfig.yaml`).<br>

<details>
  <summary>Learn more...</summary>
  <p>
  Although you don't need to know these details now, you can find more information here:
  </p>
  <ul>
    <li><a href=https://msticpy.readthedocs.io/en/latest/getting_started/msticpyconfig.html >MSTICPy Package Configuration</a></li>
    <li><a href=https://msticpy.readthedocs.io/en/latest/getting_started/SettingsEditor.html >MSTICPy Settings Editor</a></li>
  </ul>
  <p>If you need a more complete walk-through of configuration, we have a separate notebook to help you:</p>
  <ul>
    <li><a href=https://github.com/Azure/Azure-Sentinel-Notebooks/blob/master/ConfiguringNotebookEnvironment.ipynb >Configuring Notebook Environment</a></li>
    <li>And for the ultimate walk-through of how to configure all your `msticpyconfig.yaml` settings
  see the <a href=https://github.com/microsoft/msticpy/blob/master/docs/notebooks/MPSettingsEditor.ipynb >MPSettingsEditor notebook</a></li>
    <li>The Azure-Sentinel-Notebooks GitHub repo also contains an template `msticpyconfig.yaml`, with commented-out sections
  that may also be helpful in finding your way around the settings if you want to dig into things
  by hand.</li>
  </ul>
</details>
<br>

---

## 3.1 Verifying Microsoft Sentinel settings

When you launched this notebook from Microsoft Sentinel a basic configuration file - `config.json` -
was copied to your workspace folder.<br>
You should be able to see this file in the file browser to the left.<br>
This file contains details about your Microsoft Sentinel workspace but has
no configuration settings for other external services that we need.

If you didn't have a `msticpyconfig.yaml` file in your workspace folder the
`init_notebook` function should have created one for you and populated it
with the Microsoft Sentinel workspace data taken from your config.json.

<p style="border: solid; padding: 5pt; color: white; background-color: DarkOliveGreen"><b>Tip:</b>
If you do not see a "msticpyconfig.yaml" file in your user folder, click the refresh button<br>
at the top of the file browser.
</p>

We can check this now by display the settings.

<details>
    <summary>Multiple Microsoft Sentinel workspaces...</summary>
    <p>If you have multiple Microsoft Sentinel workspaces, you can add
    them in the following configuration cell.</p>
    <p>You can choose to keep one as the default or just delete this entry
    if you always want to name your workspaces explicitly when you
    connect.
    </p>
</details>


```python
import msticpy
from msticpy.config import MpConfigFile, MpConfigEdit
import os
import pprint

mp_conf = "./msticpyconfig.yaml"

# check if MSTICPYCONFIG is already an env variable
# mp_env = os.environ.get("MSTICPYCONFIG")
# mp_conf = mp_env if mp_env and Path(mp_env).is_file() else mp_conf

if not Path(mp_conf).is_file():
    print(
        "No msticpyconfig.yaml was found!",
        "Please check that there is a config.json file in your workspace folder.",
        "If this is not there, go back to the Microsoft Sentinel portal and launch",
        "this notebook from there.",
        sep="\n"
    )
else:
    mpedit = MpConfigEdit(mp_conf)
    mpconfig = MpConfigFile(mp_conf)
    print("Configured Sentinel workspaces:")
    pprint.pprint(msticpy.settings.settings["AzureSentinel"]["Workspaces"], compact=True)

msticpy.settings.refresh_config()
```

At this stage you should only see two entries in the `Azure Sentinel\Workspaces` section:

- An entry with the name of your Microsoft Sentinel workspace
- An entry named "Default" with the same settings.

## 3.2 (Optional) Configure your Azure Cloud

If you are running in a sovereign or government cloud (i.e. not the Azure global cloud)
you must set up Azure functions to use the correct authentication and
resource management authorities.

<p style="border: solid; padding: 5pt"><b>Note:</b>
This is not required if using the Azure Global cloud (most common)
and you can skip this step.</p>

If the domain of your Microsoft Sentinel or Azure Machine learning does
not end with '.azure.com' you should set the appropriate cloud
for your organization.

If you change to a different cloud, hit **Update** and **Save Settings** to write
the changes to your configuration file.


```python
display(mpedit)
mpedit.set_tab("Azure")
```

## 3.3 Load a QueryProvider for Microsoft Sentinel

To start, we are going to load up a `QueryProvider`
for Microsoft Sentinel. The `QueryProvider` is the object you use to
querying data from MS Sentinel and make it available to view and analyze in the notebook.
There are two steps to do this:
1. Create the `QueryProvider`
2. run the `connect` function to authenticate to the Sentinel workspace.

<div style="border: solid; padding: 5pt"><b>Note:</b>
If you see a warning "Runtime dependency of PyGObject is missing" when loading the<br>
Microsoft Sentinel driver, please see the FAQ section at the end of this notebook.<br>
The warning does not impact any functionality of the notebooks.
</div>
<br>
<details>
    <summary>More about query providers...</summary>
Query results are always returned as *pandas* DataFrames. If you are new
to using *pandas* look at the **Introduction to Pandas** section at in
the **A Tour of Cybersec notebook features** notebook.
    <p>
    The query provider supports other data sources, as well as Microsoft Sentinel.</p>
<p>
Other data sources supported by the `QueryProvider` class include Microsoft Defender for Endpoint,
Splunk, Microsoft Graph API, Azure Resource Graph but these are not covered here.
    </p>
Most query providers come with a range of built-in queries
for common data operations. You can also a query provider to run custom queries against
Microsoft Sentinel data.

Once you've loaded a QueryProvider you'll normally need to authenticate
to the data source (in this case Microsoft Sentinel).
    <ul>
        <li>
 <a href=https://msticpy.readthedocs.io/en/latest/data_acquisition/DataProviders.html#instantiating-a-query-provider >MSTICPy Documentation</a>.</li>
    </ul>
</details>
<br>



```python
# Refresh any config items that might have been saved
# to the msticpyconfig in the previous steps.
msticpy.settings.refresh_config()

# Initialize a QueryProvider for Microsoft Sentinel
qry_prov = QueryProvider("AzureSentinel")
```

## 3.4 Authenticate to the Microsoft Sentinel workspace

Next we need to authenticate.

The code cell immediately following this section will start the authentication process.

In Azure ML notebooks the authentication will default to using the credentials
you used to authentication to the Azure ML workspace.

More information:

<details>
   <summary>Alternative authentication options</summary>
Instead of using the Azure ML credentials, you can opt to use
one of the following:
<ul>
    <li>Device authentication</li>
    <li>Azure CLI credentials</li>
</ul>

<p><b>Device authentication</b> uses a unique code generated on your client
as an additional authentication factor. When prompted, you copy
the code, open a browser to http://microsoft.com/devicelogin and paste
it in. Then follow the interactive authentication flow.</p>

<b>Azure CLI authentication</b> requires you to logon (in the notebook or
a terminal) before authenticating to Microsoft Sentinel
<pre>az login</pre>

<p>You can change the authentication option used when calling "connect"
with the following.<br>
To force <b>Device authentication</b> add the following parameter
to the connect call
<pre>
qry_prov.connect(ws_config, mp_az_auth=False)
</pre>
</p>
<p>
To use <b>Azure CLI authentication</b>:
<pre>
qry_prov.connect(ws_config, mp_az_auth=["cli"])
</pre>
</p>
</details>


<details>
    <summary>Using WorkspaceConfig</summary>
Loading WorkspaceConfig with no parameters will use the details
of your "Default" workspace (see the Configuring Microsoft Sentinel settings section earlier)<br>

If you want to connect to a specific workspace use this syntax:<br>
   <pre>ws_config = WorkspaceConfig(workspace="WorkspaceName")</pre>
'WorkspaceName' should be one of the workspaces defined in msticpyconfig.yaml
</details>



```python
# Get the default Microsoft Sentinel workspace details from msticpyconfig.yaml

ws_config = WorkspaceConfig()

# Connect to Microsoft Sentinel with our QueryProvider and config details
qry_prov.connect(ws_config)
```

## 3.5 Test your connection using a MSTICPy built-in Microsoft Sentinel query

To explore queries in more detail see the **A Tour of CyberSec Notebook Features** notebook.



```python
# The time parameters are taken from the qry_prov.query_prov time settings
# attribute, which provides the default query time range. You can
# change interactively this by running qry_prov.query_time.
alerts_df = qry_prov.SecurityAlert.list_alerts(start=qry_prov.query_time.start)

if alerts_df.empty:
    md("The query returned no rows for this time range. You might want to increase the time range")

# display first 5 rows of any results
alerts_df.head() # If you have no data you will just see the column headings displayed
```

# 4. Configure and test external data providers (VirusTotal and Maxmind GeoLite2)

<div style="border: solid; padding:5pt">
<b>Note: </b>
This section is optional although you are likely to need one or more Threat Intel providers.<br>
You can also choose to use AlienVault OTX, IBM XForce or the MS Sentinel TI table (if
you have configured TI import into MS Sentinel) in place of VirusTotal.<br>
Follow the same procedures for the TI provider(s) of your choice.
</div>

Many Microsoft Sentinel notebooks make use of enrichment services such as Threat Intelligence and IP geo-location. We are going to set up two providers for these in this section.

Since both providers have secret keys associated with their accounts we will also show you how to specify an Azure Key Vault to securely store these settings. This is optional - you can choose to store the keys in your msticpyconfig.yaml.


## 4.1 (Optional) Configure Azure Key Vault to store secrets

To store secrets in Azure Key Vault you need to have access to a Key Vault where you have permissions to read and write secrets.

You can read more about this
<a href=https://msticpy.readthedocs.io/en/latest/getting_started/msticpyconfig.html#specifying-secrets-as-key-vault-secrets >in the MSTICPY docs</a><br>
If you want to skip this step, you can sign up for free accounts with both VirusTotal and MaxMind, until you can take the time to
set up Key Vault storage.
</p>

You will need the following information about the Key Vault:
- Azure Tenant ID (this is usually the same as you Microsoft Sentinel tenant)
- Subscription ID that the KeyVault belongs to
- Vault Name
The ResourceGroup and AzureRegion are needed if you want to create a Key Vault using MSTICPy but are optional if the Vault has already been created.

## Instructions
1. Enter the **TenantId** and **Subscription**
2. Enter the **Vault Name** - note: this is simple name, not the full URI of the Vaul.
3. Click **Update**
4. Click **Save Settings**



```python
display(mpedit)
mpedit.set_tab("Key Vault")
```


## 4.2 Configure and test Virus Total
We are going to use [VirusTotal](https://www.virustotal.com) (VT) as an example of a popular threat intelligence source.
To use VirusTotal threat intel lookups you will need a VirusTotal account and API key.

You can sign up for a free account at the
[VirusTotal getting started page](https://developers.virustotal.com/v3.0/reference#getting-started) website.

If you are already a VirusTotal user, you can, of course, use your existing key.

<p style="border: solid; padding: 5pt; color: black; background-color: Khaki">
<b>Warning</b> If you are using a VT enterprise key we do not recommend storing this
in the msticpyconfig.yaml file.<br>
MSTICPy supports storage of secrets in
Azure Key Vault if you configured this in the previous step.


As well as VirusTotal, we also support a range
of other threat intelligence providers. You can read more about that here:
[MSTICPy TI Providers](https://msticpy.readthedocs.io/en/latest/data_acquisition/TIProviders.html)

### Instructions

To add the VirusTotal details, run the following cell.

1. Select "VirusTotal" from the **Add prov** drop down
2. Click the **Add** button
3. In the left-side Details panel select **Text** as the Storage option.
4. Paste the API key in the **Value** text box.
5. Click the **Update** button to confirm your changes.

Your changes are not yet saved to your configuration file. To
do this, click on the **Save Settings** button at the bottom of the dialog.

If you are unclear about what anything in the configuration editor means, use the **Help** drop-down. This
has instructions and links to more detailed documentation.



```python
mpe = msticpy.MpConfigEdit()
mpe
```


```python
display(mpedit)
mpedit.set_tab("TI Providers")
```

Our notebooks commonly use IP geo-location information.
In order to enable this we are going to set up [MaxMind GeoLite2](https://www.maxmind.com)
to provide geolocation lookup services for IP addresses.

GeoLite2 uses a downloaded database which requires an account key to download.
You can sign up for a free account and a license key at
[The Maxmind signup page - https://www.maxmind.com/en/geolite2/signup](https://www.maxmind.com/en/geolite2/signup).
<br>

<details>
    <summary>Using IPStack as an alernative to GeoLite2...</summary>
    <p>
    For more details see the
    <a href=https://msticpy.readthedocs.io/en/latest/data_acquisition/GeoIPLookups.html >
    MSTICPy GeoIP Providers documentation</a>
    </p>
</details>
<br>

Once, you have an account, run the following cell to add the Maxmind GeopIP Lite details to your configuration.

### Instructions

The procedure is similar to the one we used for VirusTotal:

1. Select the "GeoIPLite" provider from the **Add prov** drop-down
2. Click **Add**
3. Select **Text** Storage and paste the license (API/Auth) key into the text box
4. Click **Update**
5. Click **Save Settings** to write your settings to your configuration.



```python
display(mpedit)
mpedit.set_tab("GeoIP Providers")
```

---

## 4.1. Testing VirusTotal Lookup

Threat intelligence and IP location are two common enrichments that you might apply to queried data.

Let's test the VirusTotal provider with a known bad IP Address.

<details>
    <summary>Learn more...</summary>
    <p>
    </p>
    <ul>
        <li>More details are shown in the <i>A Tour of Cybersec notebook features</i> notebook</li>
        <li><a href=https://msticpy.readthedocs.io/en/latest/data_acquisition/TIProviders.html >Threat Intel Lookups in MSTICPy</a></li>
    </ul>
</details>
<br>


```python
# Refresh any config items that saved
# to the msticpyconfig in the previous steps.
msticpy.settings.refresh_config()

# Create our TI provider
ti = TILookup()

# Lookup an IP Address
ti_resp = ti.lookup_ioc("85.214.149.236", providers=["VirusTotal"])

ti_df = ti.result_to_df(ti_resp)
ti.browse_results(ti_df, severities="all")
```

## 4.2 Test IP geolocation lookup with Maxmind GeoLite2

<div style="border: solid; padding: 5pt"><b>Note:</b>
You may see the GeoLite driver downloading its database the first time you run this.
</div>
<br>
<details>
    <summary>Learn more about MSTICPy GeoIP providers...</summary>
    <p>
    <a href=https://msticpy.readthedocs.io/en/latest/data_acquisition/GeoIPLookups.html >MSTICPy GeoIP Providers</a>
    </p>
</details>
<br>



```python
geo_ip = GeoLiteLookup()
raw_res, ip_entity = geo_ip.lookup_ip("85.214.149.236")
display(ip_entity[0])
```

---

# 5. Conclusion and Next Steps

In this notebook, we've gone through the basics of installing MSTICPy and setting up configuration.
We also briefly introduced:

- QueryProviders and querying data from Microsoft Sentinel
- Threat Intelligence lookups using VirusTotal
- Geo-location lookups using MaxMind GeoLite2

## Next Steps
We encourage you to run through the **A Tour of Cybersec notebook features** notebook
to get a better feel for some more of the capabilities of notebooks and MSTICPy.</br>

This notebook includes:

- more examples of queries
- visualizing your data
- brief introduction to using panda to manipulate your data.

Also try out some of the other Microsoft Sentinel notebooks:

- Data Visualization:
    - A Tour of Cybersec notebook features
- Investigation:
    - Guided Triage - Alerts
- Hunting:
    - Entity Explorer - Account
    - Entity Explorer - Windows Host
    - Entity Explorer - Domain and URL
- Simple Machine Learning:
    - Machine Learning in Notebooks Examples

Also check out some of the other sample notebooks in the [Microsoft Sentinel Notebooks GitHub repository](https://github.com/Azure/Azure-Sentinel-Notebooks)


---

# 6. Futher resources

 - [Jupyter Notebooks: An Introduction](https://realpython.com/jupyter-notebook-introduction/)
 - [Threat Hunting in the cloud with Azure Notebooks](https://medium.com/@maarten.goet/threat-hunting-in-the-cloud-with-azure-notebooks-supercharge-your-hunting-skills-using-jupyter-8d69218e7ca0)
 - [MSTICPy documentation](https://msticpy.readthedocs.io/)
 - [Microsoft Sentinel Notebooks documentation](https://docs.microsoft.com/azure/sentinel/notebooks)
 - [The Infosec Jupyterbook](https://infosecjupyterbook.com/introduction.html)
 - [Linux Host Explorer Notebook walkthrough](https://techcommunity.microsoft.com/t5/azure-sentinel/explorer-notebook-series-the-linux-host-explorer/ba-p/1138273)
 - [Why use Jupyter for Security Investigations](https://techcommunity.microsoft.com/t5/azure-sentinel/why-use-jupyter-for-security-investigations/ba-p/475729)
 - [Security Investigtions with Microsoft Sentinel & Notebooks](https://techcommunity.microsoft.com/t5/azure-sentinel/security-investigation-with-azure-sentinel-and-jupyter-notebooks/ba-p/432921)
 - [Pandas Documentation](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html)
 - [Bokeh Documentation](https://docs.bokeh.org/en/latest/)

---

# 7. FAQs

The following links take you to short articles in the Azure-Sentinel-Notebooks Wiki
that answer common questions.

- [How can I download all Azure-Sentinel-Notebooks notebooks to my Azure ML workspace?](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/How-can-I-download-all-Azure-Sentinel-Notebooks-notebooks-to-my-Azure-ML-workspace%3F)

- [Can I install MSTICPy by default on a new AML compute?](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/Can-I-install-MSTICPy-by-default-on-a-new-AML-compute%3F)

- [I see error "Runtime dependency of PyGObject is missing" when I load a query provider](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/%22Runtime-dependency-of-PyGObject-is-missing%22-error)

- [MSTICPy and other packages do not install properly when switching between the Python 3.6 or 3.8 Kernels](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/MSTICPy-and-other-packages-do-not-install-properly-when-switching-between-the-Python-3.6-or-3.8-Kernels)

- [My user account/credentials do not get cached between notebook runs - using Azure CLI](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/Caching-credentials-with-Azure-CLI)

See other FAQs here [Microsoft Sentinel Notebooks wiki](https://github.com/Azure/Azure-Sentinel-Notebooks/wiki/)
