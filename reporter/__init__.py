from django.utils.importlib import import_module

from reporter.base import *

class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

# Global dict used by register. Maps custom reports to callback classes.
registered_reports = {}

def register(report):
    if report.name in registered_reports.keys():
        raise AlreadyRegistered('Report %s is already registered.' %
                                report_name)
    registered_reports[report.name] = report

def unregister(report_name):
    if not report_name in registered_reports.keys():
        raise NotRegistered('Report %s is not registered.' % report_name)
    del registered_reports[report_name]

def get_report(report_name):
    if not report_name in registered_reports.keys():
        raise NotRegistered('Report %s is not registered.' % report_name)
    return registered_reports[report_name]

def get_list():
    """
    Returns a list of registered reports.
    """
    return registered_reports.keys()

def get_all():
    """
    Returns the registered_reports dict.
    """
    return registered_reports

LOADING = False

def autodiscover():
    """
    Modified from django.contrib.admin.__init__ to look for reports.py
    files.
    
    Auto-discover INSTALLED_APPS reports.py modules and fail silently when
    not present. This forces an import on them to register any reports they
    may want.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents a
    # reports.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an reports.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for reports.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own report registration.
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's reports.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its reports.py doesn't exist
        try:
            imp.find_module('reports', app_path)
        except ImportError:
            continue

        # Step 3: import the app's reports file. If this has errors we want
        # them to bubble up.
        import_module("%s.reports" % app)
    # autodiscover was successful, reset loading flag.
    LOADING = False

