Design Philosophy
=================

Developers should conform to our following design goals:

.. raw:: html

   <ul>
       <li>The database and user interface can be centralised for a single lab, so all lab members can use it instantly in their browser without requiring different installs.</li>
       <br>

       <li>The user interface is intuitive to use and user-friendly. Researchers can immediately start uploading, annotating, processing and analysing their experimental data.</li>
       <br>

       <li>The schema is designed to be as simple as possible while still capturing enough structure for advanced analysis.</li>
       <br>

       <li>Standard data processing and analyses are provided out of the box in the user interface.</li>
       <br>

       <li>For more tailored analyses, the python package is easily extendible.</li>
       <br>

       <li>Antelop supports a range of different hardware infrastructures, including:
       <br>
           <ul>
               <li>The choice between self-hosting the database or using web services such as AWS.</li>
               <br>
               <li>Support for a number of computational environments, including the option to run heavy computations on a HPC, a dedicated computing server, or locally.</li>
               <br>
               <li>The choice of a persistent web interface on a dedicated server, or running the GUI locally like a Jupyter notebook.</li>
           </ul>
       </li>
       <br>

       <li>The setup is made as simple as possible, namely:
       <br>
           <ul>
               <li>The MySQL database and S3 store can be installed and configured quickly via docker containers.</li>
               <br>
               <li>The cluster pipelines run on Nextflow with all dependencies containerised, and we provide a simple install script to configure and set this up.</li>
               <br>
               <li>The user interface and python package can be installed locally via pip, and are configured via a simple command line tool or a toml file.</li>
           </ul>
       </li>
       <br>

       <li>The benefits of a SQL database all apply, including:
       <br>
           <ul>
               <li>Centralised data storage for the lab.</li>
               <br>
               <li>Simple management of user permissions.</li>
               <br>
               <li>Easy sharing of data with collaborators.</li>
               <br>
               <li>The ability to perform automated/manual backups of the entire database.</li>
               <br>
               <li>Very fast and flexible database queries.</li>
           </ul>
       </li>
   </ul>
