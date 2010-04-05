from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist

import reporter

class AdminLogReport(reporter.BaseReport):
    """
    Send full admin log info for the day, broken down by user
    """
    name = 'admin_log'
    frequencies = ['daily', 'weekly', 'monthly']
    
    def get_default_recipients(self):
        return ['brandon.konkle@gmail.com']
    
    def get_email_subject(self):
        return '[%s] Admin log for %s' % (self.frequency.capitalize(),
                                          self.date)
    
    def get_data(self):
        data = [['Username', 'Time', 'Action', 'Content Type', 'ID', 'Name']]
        actions = { 1: 'Add',
                    2: 'Change',
                    3: 'Delete', }
        
        if self.frequency == 'daily':
            logs = LogEntry.objects.filter(
                action_time__day=self.date.day,
                action_time__month=self.date.month,
                action_time__year=self.date.year,
            ).order_by('user')
        elif self.frequency == 'weekly':
            logs = LogEntry.objects.filter(
                action_time__lt=self.tomorrow,
                action_time__gt=self.one_week,
            ).order_by('user')
        elif self.frequency == 'monthly':
            logs = LogEntry.objects.filter(
                action_time__lt=self.tomorrow,
                action_time__gt=self.one_month,
            ).order_by('user')
        
        for log in logs:
            objtype = log.content_type.name
            ct = log.content_type
            mklass = ct.model_class()
            
            try:
                if log.object_id == u"None":
                    raise ObjectDoesNotExist
                obj = mklass.objects.get(pk=log.object_id)
                obj_name = unicode(obj).encode('utf-8').replace(
                    "\n","").replace("\r","")
            except ObjectDoesNotExist:
                obj_name = u"Object gone."
            
            time = log.action_time.strftime("%H:%M")
            
            data.append([log.user, time, actions[log.action_flag],
                         log.content_type.name, log.object_id, obj_name])
        
        return data

reporter.register(AdminLogReport)
