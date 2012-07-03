launchbox
=========

Bundle cookbooks for use by chef-solo.

Launchbox supports transitive dependency resolution, chef version
contraints and exclusions (for those misbehaved cookbooks that depend on
more than they should).

Input
-----

launchbox will look for YAML files under the ``roles`` and ``mixins`` in
the input directory (which defaults to ``./src``).

An example role will look like:

::

    ci:
      include_mixins: [java]
      jenkins:
        http_proxy:
          variant: nginx
      cookbooks:
        java: "1.5.1"
        nginx: "0.101.1"
        jenkins: "0.6.3"
      run_list:
        - java
        - jenkins

Think of mixins as partial roles for reusability. At run-time launchbox
will apply all mixins in order and then override any values with the
data in the role itself.

Cookbooks
---------

The cookbooks specified for a role will be downloaded from the specified
web server or S3 bucket.

S3
~~

To use an S3 remote use ``launchbox --bucket your.bucket.name``

In the case of an S3 remote ``launchbox`` will look for the following
keys when downloading cookbooks:

::

    contents: cookbooks/<cookbook>/<version>/<cookbook>.tar.gz
    metadata: cookbooks/<cookbook>/<version>/<cookbook>.json


For determining the available versions ``launchbox`` will list
the bucket and find all available versions.

HTTP
~~~~

To use an HTTP(S) remote use
``lauchbox --url http://your/bucket/server``

In the case of an HTTP(s) remote ``launchbox`` will use the following URLs:

::

    contents: <URL>/<cookbook>/<version>/<cookbook>.tar.gz
    metadata: <URL>/<cookbook>/<version>/<cookbook>.json
    versions: <URL>/<cookbook>/versions.json


Output
------

After running launchbox the target folder will contain a JSON file with
the role metadata and tar.gz containing all the necessary cookbooks for
that role. It will also output the ``SHA-256`` of these two files.

You can supply these two files directly to ``chef-solo`` using ``-j
<path/to/role.json>`` and ``-r </path/to/role.tar.gz>``

Usage
-----

For detailed usage information please run ``launchbox -h``
