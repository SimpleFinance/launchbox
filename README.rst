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

In the case of an S3 remote ``launchbox`` will look for keys of the form
``cookbooks/<cookbook>/<version>/<cookbook>.tar.gz`` for the cookbook
contents, and ``cookbooks/<cookbook>/<version>/<cookbook>.json`` for the
metadata. For determining the available versions ``launchbox`` will list
the bucket and find all available versions.

HTTP
~~~~

To use an HTTP(S) remote use
``lauchbox --url http://your/bucket/server``

In the case of an HTTP(s) remote ``launchbox`` will download cookbook
data from
``http://example.com/cookbooks/<cookbook>/<version>/<cookbook>.tar.gz``,
cookbook metadata from
``http://example.com/cookbooks/<cookbook>/<version>/<cookbook>.tar.gz``
and the list of available cookbook versions from
``http://example.com/cookbooks/<cookbook>/versions.json``

Output
------

After running launchbox the target folder will contain a JSON file with
the role metadata and tar.gz containing all the necessary cookbooks for
that role.

Usage
-----

For detailed used information run

::

    launchbox -h
