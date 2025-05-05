[![Gitlab CI](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/badges/main/pipeline.svg)](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/-/pipelines)
[![codecov](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/badges/main/coverage.svg)](https://gitlab.com/odoo-openupgrade-wizard/odoo-openupgrade-wizard/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/odoo-openupgrade-wizard)
![PyPI - Downloads](https://img.shields.io/pypi/dm/odoo-openupgrade-wizard)
![GitLab last commit](https://img.shields.io/gitlab/last-commit/34780558)
![GitLab stars](https://img.shields.io/gitlab/stars/34780558?style=social)

# odoo-openupgrade-wizard

Odoo Openupgrade Wizard is a tool that helps developers to make major
upgrade of Odoo Community Edition. (formely OpenERP).
It works with Openupgrade OCA tools. (https://github.com/oca/openupgrade)

this tool is useful for complex migrations:
- migrate several versions
- take advantage of the migration to install / uninstall modules
- execute sql requests or odoo shell scripts between each migration
- analyse workload

It will create a migration environment (with all the code available)
and provides helpers to run (and replay) migrations until it works.

* To develop and contribute to the library, refer to the ``DEVELOP.md`` file.
* Refer to the ``ROADMAP.md`` file to see the current limitation, bugs, and task to do.
* See authors in the ``CONTRIBUTORS.md`` file.

# Table of Contents

* [Installation](#installation)
* [Usage](#usage)
    * [Command ``init``](#command-init)
    * [Command ``pull-submodule``](#command-pull-submodule)
    * [Command ``get-code``](#command-get-code)
    * [Command ``guess-requirement``](#command-guess-requirement)
    * [Command ``docker-build``](#command-docker-build)
    * [Command ``run``](#command-run)
    * [Command ``install-from-csv``](#command-install-from-csv)
    * [Command ``upgrade``](#command-upgrade)
    * [Command ``generate-module-analysis``](#command-generate-module-analysis)
    * [Command ``estimate-workload``](#command-estimate-workload)
    * [Command ``psql``](#command-psql)
    * [Command ``copydb``](#command-copydb)
    * [Command ``dropdb``](#command-dropdb)
    * [Command ``dumpdb``](#command-dumpdb)

<a name="installation"/>

# Installation

**Prerequites:**

* The tools run on debian system
* You should have docker installed on your system
* Some features require extra packages. To have all the features available run:

**Installation:**

The library is available on [PyPI](https://pypi.org/project/odoo-openupgrade-wizard/).

To install it simply run :

``pipx install odoo-openupgrade-wizard``

(See alternative installation in ``DEVELOP.md`` file.)

<a name="usage"/>

# Usage

**Note:**

the term ``odoo-openupgrade-wizard`` can be replaced by ``oow``
in all the command lines below.

<a name="command-init"/>

## Command: ``init``

```shell
odoo-openupgrade-wizard init\
  --initial-version=10.0\
  --final-version=12.0\
  --project-name=my-customer-10-12\
  --extra-repository=OCA/web,OCA/server-tools
```

Initialize a folder to make a migration from a 10.0 and a 12.0 database.
This will generate the following structure :

```
filestore/
log/
    2022_03_25__23_12_41__init.log
    ...
postgres_data/
scripts/
    step_1__update__10.0/
        pre-migration.sql
        post-migration.py
    step_2__upgrade__11.0/
        ...
    step_3__upgrade__12.0/
        ...
    step_4__update__12.0/
        ...
src/
    env_10.0/
        extra_debian_requirements.txt
        Dockerfile
        odoo.conf
        extra_python_requirements.txt
        repos.yml
        src/
    env_11.0/
        ...
    env_12.0/
        ...
config.yml
modules.csv
```

* ``config.yml`` is the main configuration file of your project.

* ``modules.csv`` file is an optional file. You can fill it with the list
  of your modules installed on your production. The first column of this
  file should contain the technical name of the module.

* ``log`` folder will contains all the log of the ``odoo-openupgrade-wizard``
  and the logs of the odoo instance that will be executed.

* ``filestore`` folder will contains the filestore of the odoo database(s).

* ``postgres_data`` folder will be used by postgres docker image to store
  database.

* ``scripts`` folder contains a folder per migration step. In each step folder:
  - ``pre-migration.sql`` can contains extra SQL queries you want to execute
    before beginning the step.
  - ``post-migration.py`` can contains extra python command to execute
    after the execution of the step.
    Script will be executed with ``odoo shell`` command. All the ORM is available
    via the ``env`` variable.

* ``src`` folder contains a folder per Odoo version. In each environment folder:

    - ``repos.yml`` enumerates the list of the repositories to use to run the odoo instance.
      The syntax should respect the ``gitaggregate`` command.
      (See : https://pypi.org/project/git-aggregator/)
      Repo files are pre-generated. You can update them with your custom settings.
      (custom branches, extra PRs, git shallow options, etc...)

    - ``extra_python_requirements.txt`` enumerates the list of extra python libraries
      required to run the odoo instance.
      The syntax should respect the ``pip install -r`` command.
      (See : https://pip.pypa.io/en/stable/reference/requirements-file-format/)

    - ``extra_debian_requirements.txt`` enumerates the list of extra system libraries
      required to run the odoo instance.

    - ``odoo.conf`` file. Add here extra configuration required for your custom modules.
      the classical keys (``db_host``, ``db_port``, etc...) are automatically
      autogenerated.

At this step, you should change the autogenerated files. For exemple:
- you can set ``update=False`` to prevents to run an update=all, in the 'regular' steps
  (first and last steps). In that case, only SQL queries and python scripts
  will be executed during this step.

You can use default files, if you have a very simple odoo instance without custom code,
extra repositories, or dependencies...

**Note:**

- In your repos.yml, preserve ``openupgrade`` and ``server-tools`` repositories
  to have all the features of the libraries available.
- In your repos.yml file, the odoo project should be in ``./src/odoo``
  and the openupgrade project should be in ``./src/openupgrade/`` folder.

<a name="command-pull-submodule"/>

## Command: ``pull-submodule``

**Prerequites:** init + being in a git repository. (if not, you can simply run ``git init``)

if you already have a repos.yml file on github / gitlab, it can be convenient to
synchronize the repository, instead of copy paste the ``repos.yml`` manually.

In that case, you can add extra values, in the ``config.yml`` file in the section

```yaml
odoo_version_settings:
  12.0:
      repo_url: url_of_the_repo_that_contains_a_repos_yml_file
      repo_branch: 12.0
      repo_file_path: repos.yml
```

then run following command :

```shell
odoo-openupgrade-wizard pull-submodule
```

<a name="command-get-code"/>

## Command: ``get-code``

**Prerequites:** init

```shell
odoo-openupgrade-wizard get-code
```

This command will simply get all the Odoo code required to run all the steps
for your migration with the ``gitaggregate`` tools.

The code is defined in the ``repos.yml`` of each environment folders. (or in the
directory ``repo_submodule`` if you use ``pull-submodule`` feature.)

**Note**

* This step could take a big while !

**Optional arguments**

if you want to update the code of some given versions, you can provide an extra parameter:

```shell
odoo-openupgrade-wizard get-code --versions 10.0,11.0
```

<a name="command-guess-requirement"/>

## Command: ``guess-requirement``

**Prerequites:** init + get-code

```shell
odoo-openupgrade-wizard guess-requirement
```

Analyze the list of the modules defined in your ``modules.csv`` file.
For each module and each version, this command tries to parse the
according ``__manifest__.py`` file (and, if possible the according ``setup.py`` file).
Finally, it overwrite the requirements.txt files present in each env folder. (python and debian requirements).

For example, here is the content of the ``addons_python_requirements.txt`` file,
when ``barcodes_generator_abstract`` and ``l10n_fr_siret`` are installed (for V16).

```
# Required by the module(s): barcodes_generator_abstract
python-barcode

# Required by the module(s): l10n_fr_siret
python-stdnum>=1.18
```

<a name="command-docker-build"/>

## Command: ``docker-build``

**Prerequites:** init + get-code

```shell
odoo-openupgrade-wizard docker-build
```

This will build local docker images that will be used in the following steps.

At the end of this step executing the following command should show a docker image per version.


```shell
docker images --filter "reference=odoo-openupgrade-wizard-*"
```
```
REPOSITORY                                                 TAG       IMAGE ID       CREATED       SIZE
odoo-openupgrade-wizard-image---my-customer-10-12---12.0   latest    ef664c366208   2 weeks ago   1.39GB
odoo-openupgrade-wizard-image---my-customer-10-12---11.0   latest    24e283fe4ae4   2 weeks ago   1.16GB
odoo-openupgrade-wizard-image---my-customer-10-12---10.0   latest    9d94dce2bd4e   2 weeks ago   924MB
```

**Optional arguments**

* if you want to (re)build an image for some given versions, you can provide
  an extra parameter: ``--versions 10.0,12.0``

**Note**

* This step could take a big while also !


<a name="command-run"/>

## Command: ``run``

**Prerequites:** init + get-code + build

```shell
odoo-openupgrade-wizard run\
    --step 1\
    --database DB_NAME
```

Run an Odoo instance with the environment defined by the step argument.

The database will be created, if it doesn't exists.

if ``stop-after-init`` is disabled, the odoo instance will be available
at your host, at the following url : http://localhost:9069
(Port depends on your ``host_odoo_xmlrpc_port`` setting of your ``config.yml`` file)

**Optional arguments**

* You can add ``--init-modules=purchase,sale`` to install modules.

* You can add ``stop-after-init`` flag to turn off the process at the end
  of the installation.


<a name="command-install-from-csv"/>

## Command: ``install-from-csv``

**Prerequites:** init + get-code + build

```shell
odoo-openupgrade-wizard install-from-csv\
    --database DB_NAME
```

Install the list of the modules defined in your ``modules.csv`` files on the
given database.

The database will be created, if it doesn't exists.

To get a correct ``modules.csv`` file, the following query can be used:
```shell
psql -c "copy (select name, shortdesc from ir_module_module where state = 'installed' order by 1) to stdout csv" coopiteasy
```


<a name="command-upgrade"/>

## Command: ``upgrade``

**Prerequites:** init + get-code + build

```shell
odoo-openupgrade-wizard upgrade\
    --database DB_NAME
```

Realize an upgrade of the database from the initial version to
the final version, following the different steps.

For each step, it will :

1. Execute the ``pre-migration.sql`` of the step.
2. Realize an "update all" (in an upgrade or update context)
3. Execute the scripts via XML-RPC (via ``odoorpc``) defined in
   the ``post-migration.py`` file.

**Optional arguments**

* You can add ``--first-step=2`` to start at the second step.

* You can add ``--last-step=3`` to end at the third step.


<a name="command-generate-module-analysis"/>

## Command: ``generate-module-analysis``

**Prerequites:** init + get-code + build

```shell
odoo-openupgrade-wizard generate-module-analysis\
    --database DB_NAME
    --step 2
    --modules MODULE_LIST
```

Realize an analysis between the target version (in parameter via the step argument)
and the previous version. It will generate analysis_file.txt files present
in OpenUpgrade project.
You can also use this function to analyze differences for custom / OCA modules
between several versions, in case of refactoring.

<a name="command-estimate-workload"/>

## Command: ``estimate-workload``

**Prerequites:** init + get-code

```shell
odoo-openupgrade-wizard estimate-workload
```

Generate an HTML file name ``analysis.html`` with all the information regarding
the work to do for the migration.
- checks that the modules are present in each version. (by managing the
  renaming or merging of modules)
- check that the analysis and migration have been done for the official
  modules present in odoo/odoo

<a name="command-psql"/>

## Command: ``psql``

**Prerequites:** init

```shell
odoo-openupgrade-wizard psql
    --database DB_NAME
    --command "SQL_REQUEST"
```

Execute an SQL Request on the target database.

**Optional arguments**

* If no ``database`` is provided, default ``postgres`` database will be used. example:

```shell
odoo-openupgrade-wizard psql --command "\l";
```
Result:
```
                              List of databases
    Name    | Owner | Encoding |  Collate   |   Ctype    | Access privileges
------------+-------+----------+------------+------------+-------------------
 postgres   | odoo  | UTF8     | en_US.utf8 | en_US.utf8 |
 template0  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 | =c/odoo          +
            |       |          |            |            | odoo=CTc/odoo
 template1  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 | =c/odoo          +
            |       |          |            |            | odoo=CTc/odoo
 test_psql  | odoo  | UTF8     | en_US.utf8 | en_US.utf8 |

```

* if you execute request that return long result, you can choose to select ``pager`` or ``-no-pager``
  option to display the result via the click function ``echo_via_pager``.
  (see : https://click.palletsprojects.com/en/8.1.x/utils/#pager-support)

Note : Pager is enabled by default.


* you can pass extra psql arguments inline.

```shell
odoo-openupgrade-wizard psql
    --database=test_psql
    --command "select id, name from res_partner where name ilike '%admin%';"
    -H
```
Result:
```html
<table border="1">
  <tr>
    <th align="center">id</th>
    <th align="center">name</th>
  </tr>
  <tr valign="top">
    <td align="right">3</td>
    <td align="left">Administrator</td>
  </tr>
</table>
<p>(1 row)<br />
</p>

```

See all the options here https://www.postgresql.org/docs/current/app-psql.html

<a name="command-copydb"/>

## Command: ``copydb``

**Prerequites:** init

```shell
odoo-openupgrade-wizard copydb
    --source DB_NAME
    --dest NEW_DB_NAME
```

Create an Odoo database by copying an existing one.

This script copies using postgres CREATEDB WITH TEMPLATE. It also copies
the filestore.

<a name="command-dropdb"/>

## Command: ``dropdb``

**Prerequites:** init

```shell
odoo-openupgrade-wizard dropdb
    --database DB_NAME
```

Delete an Odoo database and its filestore.

This command will always success even if DB_NAME does not exists.

<a name="command-dumpdb"/>

## Command: ``dumpdb``

**Prerequites:** init

```shell
odoo-openupgrade-wizard dumpdb
    --database DB_NAME
    --database-path DATABASE_PATH
    --filestore-path FILESTORE_PATH
```

Dump the database DB_NAME to DATABASE_PATH and export the filestore
related to DB_NAME into FILESTORE_PATH. To choose the format of the
backup files look at the `--database-format` and `--filestore-format`.

*WARNING*: DATABASE_PATH should be a sub directory of the project path
in orter to have the postgresql container able to write the dump file.
For example, the project path is `/path/to/myproject` (where you run the
`init` command), then DATABASE_PATH can be any of the subdirectory of
`/path/to/myproject`.

**Optional arguments**

* To choose the database format use `--database-format`. Format can be
  one of the following:
      - `p` for plain sql text
      - `c` for custom compressed backup of `pg_dump`
      - `d` for directory structure
      - `t` for a tar version of the directory structure
  See also https://www.postgresql.org/docs/current/app-pgdump.html
  The default database format is `c`.

* To choose the filestore format use `--filestore-format`. Format can be
  one of the following:
      - `d` copy of the directory structure
      - `t` tar version of the directory structure (not compressed)
      - `tgz` tar version of the directory structure compressed with gzip.
  The default filestore format is `tgz`.

* By default, if database file or filestore file already exists, the
  command will fail, preserving the existing dump. If you need to
  overwrite the existing files, the `--force` option can be used.
