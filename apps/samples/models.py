from datetime import datetime
from django.db import models
from django.db.models.signals import post_save

from locations.models import Location
from standards.models import Standard, WaterUseType
from reporters.models import Reporter
from wqm.models import SamplingPoint
from xformmanager.models import Metadata
from hq.models import ReporterProfile
from smsnotifications.models import SmsNotification, send_sms_notifications, _send_sms
from datetime import datetime
import httplib, urllib
from threading import Thread


H2S_XMLNS = "http://www.aquatest-za.org/h2s"
PHYSCHEM_XMLNS = "http://www.aquatest-za.org/physchem"
SAMPLE_XMLNS = [H2S_XMLNS, PHYSCHEM_XMLNS]


class SampleDates(models.Model):
    """
        This module adds, modified and created dates for samples modules
    """
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())


class Parameter(SampleDates):
    test_name = models.CharField(max_length=120)
    unit = models.CharField(max_length=50, null=True, blank=True)
    lookup_hint = models.BooleanField()
    test_name_short = models.CharField(max_length=20)

    def __unicode__(self):
        return self.test_name

class Sample(SampleDates):
    '''
    This is sample
    '''
    taken_by = models.ForeignKey(Reporter)
    sampling_point = models.ForeignKey(SamplingPoint)
    notes = models.CharField(max_length=250, null=True, blank=True)
    batch_number = models.CharField(max_length=100)
    # some_field to check if this sample is new o not.
    incubated = models.BooleanField(default=False)
    date_taken = models.DateTimeField()
    date_received = models.DateTimeField()

    def __unicode__(self):
        return self.notes

#class MeasuredValue(SampleDates):
class MeasuredValue(models.Model):
    '''
    The measured values
    '''
    parameter = models.ForeignKey(Parameter)
    sample = models.ForeignKey(Sample)
    value = models.CharField(max_length=20, help_text='the value measured')

    def __unicode__(self):
        return '%s' % (self.value)


class ValueRule(SampleDates):
    '''
    Rules Applied to the values
    '''
    description = models.TextField()
    parameter = models.ForeignKey(Parameter, unique=True)
    standard = models.ForeignKey(Standard)
    water_use_type = models.ForeignKey(WaterUseType)

    def __unicode__(self):
        return self.description

class Range(models.Model):
    """
     This class provide the range of the measured values, and the date
     created or modified.
    """
    maximum = models.IntegerField()
    minimum = models.IntegerField()
    modified = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())

class NormalRange(Range):
    '''
    Normal range for values.
    '''
    description = models.CharField(max_length=200)
    value_rule = models.ForeignKey(ValueRule)

    def __unicode__(self):
        return '%d - %d' % (self.minimum, self.maximum)

class AbnormalRange(Range):
    description = models.CharField(max_length=200)
    value_rule = models.ForeignKey(ValueRule)
    remedialaction = models.CharField(max_length=20)
    color = models.CharField(max_length=25)

    def __unicode__(self):
        return '%d - %d' % (self.minimum, self.maximum)
    
    
def check_and_add_sample(sender, instance, created, **kwargs): #get sender, instance, created
    # only process newly created forms, not all of them
    if not created:             return
    
    # check the form type to see if it is a new sample
    form_xmlns = instance.formdefmodel.target_namespace
    xform = ''
    if form_xmlns in SAMPLE_XMLNS:
        # it is an xmlns we care about, so make a new sample
        sample_data = instance.formdefmodel.row_as_dict(instance.raw_data)
        sample = Sample()
        now = datetime.now()
        
        # check for which form submitted and create a sample.
        # h2s test
        vals = []
        if form_xmlns == H2S_XMLNS:
            xform = 'h2s' #these should not be hardcoded
            point = SamplingPoint.objects.get(code = sample_data["h2s_test_assessment_pointcode"])
            sample.sampling_point = point
            sample.date_taken = sample_data["h2s_test_assessment_assessmentdate"]
            sample.notes = sample_data["h2s_test_datacapture_comments"]
            sample.date_received = now
            # sample.created = now
            
            # check the reporter using he's/her alias
            # TODO: Make sure the reporter is a tester (is have a reporter profile)
            # if he's not a tester(ie does not belong to aquatest domain) issue an error.
            alias = sample_data["h2s_test_datacapture_enteredby"]
            try:
                reporter = Reporter.objects.get(alias__iexact = alias)
                # make sure the reporter have a profile for a domain.
                # TODO: Limit the submission to a domain
                reporter_profile = ReporterProfile.objects.get(reporter=reporter)
                # save a reporter with a profile
                sample.taken_by = reporter
            except Exception, e:
                raise

            # Note:
            # this save makes the sample signal to be called with out the measured values
            sample.save()
            
            # generate test result column from the registered paramater
            parameters = Parameter.objects.all()
            # initialise the tests, inorder for the index to eqaul the pk of
            # the parameter. ( a better way of refering to a parameter shuld
            # be looked upon).
            tests = [None] * 100 # TODO: Initialise the tests (multiply wit some big number)
            for para in parameters:
                test = "h2s_test_testresults_" + para.test_name_short
                index = int(para.pk)
                tests.insert(index, test)

            
            for some in tests:
                if sample_data.get(some) != None:
                    para_id = tests.index(some)
                    # print " >>>>>>>>>>> index : %s " % tests.index(some)
                    # print Parameter.objects.get(id=tests.index(some))

                    # this test is present in the xform, hence store it's value.
                    value = MeasuredValue()
                    value.value = sample_data[some]

                    # TODO: get a parameter for the value. according to the test done.
                    value.parameter = Parameter.objects.get(id = para_id)
                    value.sample = sample
                    value.save()
                    vals.append(value)
            
        # physical chemical test
        if form_xmlns == PHYSCHEM_XMLNS:
            xform = 'physchem' #these should not be hardcoded
            point = SamplingPoint.objects.get(code = sample_data["physchem_test_assessment_pointcode"])
            sample.sampling_point = point
            sample.date_taken = sample_data["physchem_test_assessment_assessmentdate"]
            sample.notes = sample_data["physchem_test_datacapture_comments"]
            sample.date_received = now
            sample.created = now

            alias = sample_data["physchem_test_datacapture_enteredby"]
            try:
                reporter = Reporter.objects.get(alias__iexact = alias)
                # make sure the reporter have a profile for a domain.
                # TODO: Limit the submission to a domain
                reporter_profile = ReporterProfile.objects.get(reporter=reporter)
                # save a reporter with a profile
                sample.taken_by = reporter
            except Exception, e:
                raise

           # Note:
           # this save makes the sample signal to be called with out the measured values

            sample.save()

            # generate test result column from the registered paramater
            parameters = Parameter.objects.all()
            # initialise the tests, inorder for the index to eqaul the pk of
            # the parameter. ( a better way of refering to a parameter shuld
            # be looked upon).
            
            tests = [None] * 100 # TODO: Initialise the tests (multiply wit some big number)
            for para in parameters:
                test = "physchem_test_testresults_" + para.test_name_short
                if sample_data.get(test) == None: # a simple check to get temperature and weather assements
                    test =  "physchem_test_assessment_" + para.test_name_short
                index = int(para.pk)
                tests.insert(index, test)
            
            # TODO: ['physchem_test_assessment_temperature'] ['physchem_test_assessment_weather']
            # shuld this be in test parameter or in the notes??

            # empty list for measured values
            
            for some in tests:
                if sample_data.get(some) != None:
                    para_id = tests.index(some)
                    
                    # this test is present in the xform, hence store it's value.
                    value = MeasuredValue()
                    value.value = sample_data[some]

                    # TODO: get a parameter for the value. according to the test done.
                    value.parameter = Parameter.objects.get(id = para_id)
                    value.sample = sample
                    value.save()
                    vals.append(value)
    # A function to send sms notification.
#    send_event_google_calender('hall 4','fred usiku','h2s')
    send_sms_notifications(sample,vals,xform)
#    send_event_google_calender('sample.sampling_point','sample.taken_by','h2s')
    
#    alert_google_calendar(sample,vals)
# Register to receive signals each time a Metadata is saved
    
post_save.connect(check_and_add_sample, sender=Metadata)

