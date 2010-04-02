from __future__ import with_statement
import os
import sys
import csv
import datetime

from django.core.mail import EmailMessage
from django.contrib.sites.models import Site
from django.conf import settings

TMP_DIR = getattr(settings, 'TMP_DIR', '/tmp')

class BaseReport(object):
    "A base class for reports to subclass."
    def __init__(self, date=None, view=False, filename=None, recipients=None,
                 report_args=None):
        modules = self.__module__.split('.')
        self.name = modules[len(modules) - 1]
        frequency = modules[len(modules) - 2]
        if not frequency in ('daily', 'weekly', 'monthly'):
            raise NotImplementedError(
                'This is a base class, and it cannot be directly initialized.'
            )
        self.frequency = frequency
        self.set_dates(date)
        self.view = view
        self.send = True
        if filename or view:
            self.send = False
        self.file = self.get_file(filename)
        self.recipients = None
        if recipients:
            self.recipients = recipients
        self.site = Site.objects.get_current()
        self.args = report_args
    
    def get_file(self, filename):
        """
        Return an appropriate file object.
        """
        if self.view:
            return sys.stdout
        if not filename:
            filename = '%s/report.%s.%s.%s.csv' % (TMP_DIR, self.frequency,
                                                   self.name, self.date)
        return open(filename, 'w')
    
    def set_dates(self, date):
        """
        Set the dates to be used in the report. This assigns the following
        attributes to the class:
            tomorrow - 1 day from today or the given date
            one_week - 7 days prior to today or the given date
            one_month - 32 days prior to today or the given date
        """
        if type(date) is datetime.date:
            self.date = date
        else:
            self.date = datetime.date.today()
        self.tomorrow = self.date + datetime.timedelta(days=1)
        self.one_week = self.date - datetime.timedelta(days=7)
        self.one_month = self.date - datetime.timedelta(days=32)
    
    def get_default_recipients(self, recipients):
        """
        Get the default recipients for the report. Should return a list of
        email addresses.
        """
        raise NotImplementedError
    
    def get_data(self):
        "Get the data that is emailed in the report. Should return a string."
        raise NotImplementedError
    
    def get_email_subject(self):
        """
        Get the subject for the email sent with the results. Should return a
        string.
        """
        raise NotImplementedError
    
    def run_report(self):
        "Run the report itself, converting the data into a csv file."
        w = csv.writer(self.file)
        w.writerows(self.get_data())
        self.file.close()
        if self.send:
            self.send_results()
    
    def send_results(self):
        "Send the results to the appropriate email addresses."
        if not self.recipients:
            self.recipients = self.get_default_recipients()
        with open(self.file.name) as f:
            subject = self.get_email_subject()
            message = EmailMessage(
                subject=subject,
                body='Please review the attached report.\n\n',
                from_email='webmaster@pegasusnews.com',
                to=self.recipients,
                attachments=[('%s.%s.csv' % (self.name, self.date),
                              f.read(), 'text/plain')]
            )
        message.send()
        os.remove(self.file.name)

from django.utils.importlib import import_module

LOADING = False

def autodiscover():
    """
    Copied & pasted from django/contrib/admin/__init__.py and altered to look
    for site-specific admin.py files. It will look for SITE_admin.py for each
    app where SITE is the site name passed to the function.
    
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # admin.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an admin.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module('%s_admin' % site, app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        import_module("%s.%s_admin" % (app, site))
    # autodiscover was successful, reset loading flag.
    LOADING = False
    
