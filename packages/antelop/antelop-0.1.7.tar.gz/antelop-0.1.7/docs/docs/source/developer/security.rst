Security and configuration
==========================

Antelop has a number of interacting components, so it is therefore worth briefly discussing some of the security and configuration considerations that we have taken into account when developing the software.

Database credentials
--------------------

We use the following database accounts for the MySQL database and S3 object store:

* The root user, whose credentials should obviously be kept securely by the database administrator.
* Users with SELECT, INSERT, DELETE and UPDATE priviledges on all Antelop tables, with one MySQL user per lab member. 
* Optional additional users with just SELECT priviledges for sharing data with collaborators.

These define the credentials used by the webapp and nextflow pipelines to connect to the database. We use identical credentials for the MySQL and S3 databases.

We enforce further permissions at the application level. It is therefore important that users only access antelop through the gui or python interface - they could bypass these application level permissions if they connect through a different MySQL client. This is why it is also important to only share these credentials with trusted users such as lab members. If you need to share data more widely with collaborators, then use a user with just SELECT priviledges.

.. _permissions:

Application permissions
-----------------------

The application level privileges are enforced in the `src/antelop/connection/permission.py` script. Whenever a user logs in, the DataJoint tables are modified in this script to override the built in DataJoint methods such as insert and delete, to enforce our permissions. Furthermore, some permissions are also enforced inside the gui, such as what page a user can access. This is not necessary to protect the database but simply helps a user understand what actions they can and cannot perform.

Of particular importance is the `Experimenter` table. This table should corresond one-to-one with MySQL users. Data ownership is enforced via inheritance from this table. All tables in antelop inherit from this tables, so all data entries have the `experimenter` primary key attribute. Comparison of this attribute with the logged in username is how permissions are enforced.

We also introduce the concept of temporary deletes. All tables have the `tablename_deleted` attribute, which can be True or False. Temporary deletes simply correspond to changing this attribute. The gui reads this attribute and displays only non-temporarily deleted data, so it acts like a full delete, but administrators have the ability to recover data. There are some considerations here concerning database integrity; ie, how to ensure no non-deleted data has deleted parents, which is discussed in :ref:`admin`.

At the application level, we distinguish between administrators and regular users, via the `admin` column in the `Experimenter` table. Regular users can fetch any data in the database. They can perform inserts and updates on data that belongs to them. They can also temporary delete their own data. Administrators can restore temporarily deleted data, and can permanently delete any temporarily deleted data. This means a true delete requires two steps: first, the user must temporary delete it, then the admin must permanently delete it.

HPC connection
--------------

The final security point worth mentioning is that when a user submits a computational job to run, the GUI needs to issue a command to the cluster entry node, or other compute server, telling it to run the predefined Nextflow pipeline. To do this, we use the `paramiko` python package to issue the command via ssh. This is also necessary in the containerised shared machine deployment to shell out of the container to execute the pipeline on the host. The cluster entry node or compute server address is pre-configured by the user in the configuration file, or in the desktop app deployment, it just SSHs to the host the container is run on. The user needs to manually enter their password, through streamlit's text_input widget in password mode. We decided it is not secure to store these credentials anywhere at all, and it acts as a good check for the user that they really want to submit that job anyway. At present, we use the exact same usernames in antelop as the user has on the HPC - this can be easily changed if necessary to add a username input widget too.

The database credentials are injected into the nextflow pipeline environment as environment variables when triggered from the GUI, then called inside nextflow as environment variables to be injected into the work environment for each process on the HPC, so they can be accessed by the scripts that need to interact with the database.
