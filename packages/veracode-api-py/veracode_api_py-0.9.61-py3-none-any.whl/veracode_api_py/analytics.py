#analytics.py - API class for Analytics Reporting API calls

import json
from uuid import UUID

from .apihelper import APIHelper

class Analytics():
   report_types = [ "findings", "scans", "deletedscans" ]

   findings_scan_types = ["Static Analysis", "Dynamic Analysis", "Manual", "SCA", "Software Composition Analysis" ]
   scan_scan_types = ["Static Analysis", "Dynamic Analysis", "Manual" ]

   base_url = 'appsec/v1/analytics/report'

   #public methods
   def create_report(self,report_type,last_updated_start_date=None,last_updated_end_date=None,
                     scan_type:list = [], finding_status=None,passed_policy=None,
                     policy_sandbox=None,application_id=None,rawjson=False, deletion_start_date=None,
                     deletion_end_date=None, sandbox_ids:list = []):

      if report_type not in self.report_types:
         raise ValueError("{} is not in the list of valid report types ({})".format(report_type,self.report_types))

      report_def = { 'report_type': report_type }

      if last_updated_start_date:
         report_def['last_updated_start_date'] = last_updated_start_date
      else:
         if report_type in ['findings','scans']:
            raise ValueError("{} report type requires a last updated start date.").format(report_type)

      if last_updated_end_date:
         report_def['last_updated_end_date'] = last_updated_end_date
         
      if deletion_end_date:
         report_def['deletion_end_date'] = deletion_end_date

      if deletion_start_date:
         report_def['deletion_start_date'] = deletion_start_date
      else:
         if report_type == 'deletedscans':
            raise ValueError("{} report type requires a deleteion start date.").format(report_type)

      if len(scan_type) > 0:
         if report_type == 'findings':
            valid_scan_types = self.findings_scan_types
         elif report_type in [ 'scans', 'deletedscans' ]:
            valid_scan_types = self.scan_scan_types
         if not(self._case_insensitive_list_compare(scan_type,valid_scan_types)):
            raise ValueError("{} is not in the list of valid scan types ({})".format(scan_type,valid_scan_types))
         report_def['scan_type'] = scan_type

      if finding_status:
         report_def['finding_status'] = finding_status

      if passed_policy:
         report_def['passed_policy'] = passed_policy

      if policy_sandbox:
         report_def['policy_sandbox'] = policy_sandbox

      if application_id:
         report_def['application_id'] = application_id

      if sandbox_ids:
         report_def['sandbox_ids'] = sandbox_ids
      
      payload = json.dumps(report_def)
      response = APIHelper()._rest_request(url=self.base_url,method="POST",body=payload)

      if rawjson:
         return response
      else:
         return response['_embedded']['id'] #we will usually just need the guid so we can come back and fetch the report

   def get_findings(self, guid: UUID):
      thestatus, thefindings = self.get(guid=guid,report_type='findings')
      return thestatus, thefindings

   def get_scans(self, guid: UUID):
      thestatus, thescans = self.get(guid=guid,report_type='scans')
      return thestatus, thescans

   def get_deleted_scans(self, guid: UUID):
      thestatus, thescans = self.get(guid=guid,report_type='deletedscans')
      return thestatus, thescans   
   
   def get(self,guid: UUID,report_type='findings'):
      # handle multiple scan types
      uri = "{}/{}".format(self.base_url,guid)
      theresponse = APIHelper()._rest_paged_request(uri,"GET",report_type,{},fullresponse=True)
      thestatus = theresponse.get('_embedded',{}).get('status','')
      thebody = theresponse.get('_embedded',{}).get(report_type,{})
      return thestatus, thebody

   #helper methods
   def _case_insensitive_list_compare(self,input_list:list, target_list:list):
      input_set = self._lowercase_set_from_list(input_list)
      target_set = self._lowercase_set_from_list(target_list)
      return target_set.issuperset(input_set)

   def _lowercase_set_from_list(self,thelist:list):
      return set([x.lower() for x in thelist])