import os
import datetime
import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module

import reporter

class Command(BaseCommand):
    help = ('Runs reports, which are registered in reports.py files within'
            'installed apps. Valid frequencies are "daily", "weekly", and '
            '"monthly". By default, the reports are emailed to the report\'s '
            'default recipients. This can be overridden through options.  '
            'Additional arguments after the report name will be passed to '
            'the report.')
    
    args = 'FREQUENCY REPORT_NAME [REPORT ARGS]'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '-V', '--view',
            action='store_true',
            dest='view',
            help=('Send the data to stdout instead of emailing or saving to a'
                  ' file.')
        ),
        make_option(
            '-f', '--filename',
            action='store',
            dest='filename',
            metavar='FILE',
            help=('Instead of emailing the results, save them to the provided'
                  ' filename.')
        ),
        make_option(
            '-r', '--recipients',
            action='store',
            dest='recipients',
            metavar='RECIPIENTS',
            help=('Override the default recipients for the report. Seperate '
                  'each email address with a comma. Do not use spaces.')
        ),
        make_option(
            '-l', '--list-all',
            action='store_true',
            dest='list_all',
            help='List all available reports, and then exit.'
        ),
        make_option(
            '-d', '--date',
            action='store',
            dest='date',
            metavar='YYYY-MM-DD',
            help='Provide a date to run the report for.'
        ),
    )
    
    def handle(self, *args, **options):
        # Autodiscover all reports by scanning INSTALLED_APPS for reports.py
        # files.
        reporter.autodiscover()
        
        if options.get('list_all', False):
            # List all reports, printing their docstrings
            print "Listing all available reports:"
            available_reports = reporter.get_all()
            frequencies = ['daily', 'weekly', 'monthly']
            for frq in frequencies:
                reports_found = []
                for report_name, report in available_reports.items():
                    if frq in report.frequencies:
                        reports_found.append('    %s - %s' %
                                             (report_name,
                                              report.__doc__.strip()))
                if reports_found:
                    print '\n%s:' % frq.capitalize()
                    for report in reports_found:
                        print report
            print ('\nFor more information on how to run reports, use this '
                   'command with the -h option.')
            exit(0)
        
        # Make sure the right number of arguments was provided
        if len(args) < 2:
            raise CommandError('Please provide both a frequency and a '
                               'report name.')
        if not args[0] in ('daily', 'weekly', 'monthly'):
            raise CommandError('Please provide a valid frequency.')
        
        frequency = args[0]
        name = args[1]
        report_args = None
        if len(args) > 2:
            report_args = args[2:]
        date = options.get('date', None)
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            date = datetime.date(date.year, date.month, date.day)
        filename = options.get('filename', None)
        view = options.get('view', False)
        recipients = options.get('recipients', None)
        if recipients:
            recipients = recipients.split(',')
        
        try:
            report_class = reporter.get_report(name)
            report = report_class(frequency, date, view, filename, recipients,
                                  report_args)
        except (reporter.NotRegistered, reporter.NotAvailable), e:
            raise CommandError(e)
        report.run_report()
