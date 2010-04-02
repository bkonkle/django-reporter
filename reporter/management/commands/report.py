import os
import datetime
import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.importlib import import_module

REPORT_MODULE_PREFIX = 'reporter.reports'

class Command(BaseCommand):
    help = ('Runs reports, which are collected in the '
            'reporter module. Valid frequencies are "daily", '
            '"weekly", and "monthly". By default, the reports are emailed to '
            "the report's default recipients. This can be overridden through "
            'options.  Additional arguments after the report name will be '
            'passed to the report.')
    
    args = 'FREQUENCY REPORT_NAME [REPORT ARGS]'
    
    option_list = BaseCommand.option_list + (
        make_option(
            '--view',
            action='store_true',
            dest='view',
            help=('Send the data to stdout instead of emailing or saving to a'
                  ' file.')
        ),
        make_option(
            '--filename',
            action='store',
            dest='filename',
            metavar='FILE',
            help=('Instead of emailing the results, save them to the provided'
                  ' filename.')
        ),
        make_option(
            '--recipients',
            action='store',
            dest='recipients',
            metavar='RECIPIENTS',
            help=('Override the default recipients for the report. Seperate '
                  'each email address wth a comma. Do not use spaces.')
        ),
        make_option(
            '--list-all',
            action='store_true',
            dest='list_all',
            help=('List all available reports, and then exit. If a report has'
                  ' not yet been converted to the new format, it will have '
                  'the words (Invalid) printed next to it.')
        ),
        make_option(
            '--date',
            action='store',
            dest='date',
            metavar='YYYY-MM-DD',
            help=('Provide a date to run the report for.')
        ),
    )
    
    def handle(self, *args, **options):
        if options.get('list_all', False):
            # Discover and list all reports, checking their validity
            from reporter import reports
            from reporter.utils import locate
            print "Listing all available reports:\n"
            reports_found = {}
            frequencies = ['daily', 'weekly', 'monthly']
            for frq in frequencies:
                reports_found[frq] = []
            for report in locate('*.py', reports.__path__[0]):
                if os.path.basename(report) == '__init__.py':
                    continue
                frequency = os.path.basename(os.path.dirname(report))
                name = os.path.basename(report)[:-3]
                module = '%s.%s.%s' % (REPORT_MODULE_PREFIX,
                                       frequency,
                                       name)
                report_module = import_module(module)
                valid = '\n        (invalid)'
                doc = ''
                if getattr(report_module, 'report', None):
                    valid = ''
                    doc = '\n        %s' % (
                        report_module.report.__doc__.strip()
                    )
                reports_found[frequency].append(
                    '    %s%s%s' % (name, valid, doc)
                )
            for frq in frequencies:
                print '%s:' % frq.capitalize()
                for report in reports_found[frq]:
                    print report
                print '\n'
            print ('For more information on how to run reports, use this '
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
        
        # Import the module for the requested report
        module = '%s.%s.%s' % (REPORT_MODULE_PREFIX, frequency, name)
        report_module = import_module(module)
        report = report_module.report(date, view, filename, recipients,
                                      report_args)
        report.run_report()
