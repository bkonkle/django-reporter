===============
Django-reporter
===============

A Django application to create automated email reports in .csv format.  It
includes a management command that is intended to be invoked periocically from
cron.

Installation
************

To install::

    pip install django-reporter

Then add ``reporter`` to your INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'reporter',
    )

Also, make sure the email settings for your project are correct.

Creating Reports
****************

Similar to Django's admin app, reports are created within *reports.py* files
inside your installed applications.  Inside each *reports.py* should be at
least one report that subclasses the ``reporter.BaseReport`` class.  After the
subclass is defined, use the ``reporter.register()`` function to register the
report.  Your subclass should define at least two attributes and implement
a few methods, detailed below.  Review the *sample_reports.py* file for an
example of a simple report.

Required Attributes
-------------------

A basic report should have a docstring (which is shown with the ``--list-all``
option on the management command), and needs at least two attributes,
``name``, and ``frequencies``.

For example, the sample report starts out with::

    class AdminLogReport(reporter.BaseReport):
        """
        Send full admin log info for the day, broken down by user
        """
        name = 'admin_log'
        frequencies = ['daily']

``name``
~~~~~~~~

.. attribute:: BaseReport.name

The name of the report, used when invoking the ``report`` management command.

``frequencies``
~~~~~~~~~~~~~~~

.. attribute:: BaseReport.frequencies

The frequencies that this report is available for.

Built-in Attributes
-------------------

The base class automatically sets a number of attributes that are available
in the subclass.

``frequency``
~~~~~~~~~~~~~

.. attribute:: BaseReport.frequency

The requested frequency of the report.  This can be used to determine the
correct date range to filter for in your report.

``date``
~~~~~~~~

.. attribute:: BaseReport.date

The requested date for the report.  Defaults to today if no date is provided.

``tomorrow``
~~~~~~~~~~~~

.. attribute:: BaseReport.tomorrow

The requested date plus 1 day.

``one_week``
~~~~~~~~~~~~

.. attribute:: BaseReport.one_week

The requested date minus 7 days.

``one_month``
~~~~~~~~~~~~~

.. attribute:: BaseReport.one_month

The requested date minus 32 days.

``args``
~~~~~~~~

.. attribute:: BaseReport.args

A list of additional arguments passed on to the report from the management
command.

Methods
-------

These methods are required to be implemented in your subclass in order to
generate reports.

``get_default_recipients``
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. method:: BaseReport.get_default_recipients(self):

This method is called by the base class's ``send_results`` method.  It
provides the default recipients for the email, which is used if the recipients
are not overridden by the ``--recipients`` option on the management command.
This should return a list of strings containing the email address of each
recipient.

``get_email_subject``
~~~~~~~~~~~~~~~~~~~~~

.. method:: BaseReport.get_email_subject(self):

This method is also called by the base class's ``send_results`` method.  It
provides the subject line for the email that is sent.  It should return a
string.

``get_data``
~~~~~~~~~~~~

This is the method that the base class calls to retrieve the data that should
be converted to csv and sent through email.  This should return a list of
rows, each row consisting of a list of fields.

For example, in the sample ``admin_log`` report, a header row is defined at
the top of the ``get_data`` method::

    data = [['Username', 'Time', 'Action', 'Content Type', 'ID', 'Name']]

Then, for each row of data, a list of data within those fields is appended::

    data.append([log.user, time, actions[log.action_flag],
             log.content_type.name, log.object_id, obj_name])

Registration
------------

Once the report is defined in the *reports.py* file, it's ready to be
registered.  The sample report registers its class at the bottom of the file::

    reporter.register(AdminLogReport)

Running Reports
***************

To run reports, use the ``report`` management command.

Usage::

    report [options] FREQUENCY REPORT_NAME [REPORT ARGS]

Valid frequencies are "daily", "weekly", and "monthly". By default, the
reports are emailed to the report's default recipients. This can be
overridden through the ``--recipients`` option.  Additional arguments after
the report name will be passed to the report.

Options
-------

``-V, --view``
~~~~~~~~~~~~~~

Send the data to stdout instead of emailing or saving to a file.

``-f FILE, --filename=FILE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of emailing the results, save them to the provided filename.

``-r RECIPIENTS, --recipients=RECIPIENTS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Override the default recipients for the report.  Seperate each email address
with a comma. Do not use spaces.

``-l, --list-all``
~~~~~~~~~~~~~~~~~~

List all available reports, and then exit.

``-d YYYY-MM-DD, --date=YYYY-MM-DD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a date to run the report for.
