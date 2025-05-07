from .base_functions import BaseFunctions
import requests
import warnings
import json
from typing import Union, List


class PostEndpoints:
    def __init__(self, label: str, data_dir: str, certificate_file: str = None, key_file: str = None, debug: bool = False):
        self.base_class = BaseFunctions(label=label, data_dir=data_dir, certificate_file=certificate_file, key_file=key_file, debug=debug)
        self.data_dir = data_dir
        self.debug = debug

    @staticmethod
    def __check_fields(data: Union[dict, List], required_fields: List, allowed_fields: List):
        if isinstance(data, dict):
            data = data.keys()

        for field in data:
            if field not in allowed_fields and field not in required_fields:
                warnings.warn('Field {field} is not implemented. Optional fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields)))

        for field in required_fields:
            if field not in data:
                raise ValueError('Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

    def post_master_action(self, data: dict, overload_fields: dict = None):
        """
        Upload the new employee to SAP through MasterAction
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ["external_employee_subgroup"]
        required_fields = ["afas_employee_id", "sap_employee_id", "start_date", "end_date", "action",
                           "reason", "employment_status", "company_code", "personal_area", "personal_sub_area",
                           "employee_group", "employee_sub_group", "sap_org_unit_id", "position_id", "cost_center", "salutation",
                           "last_name", "first_name", "prefix", "second_name_prefix", "initials",
                           "other_title", "date_of_birth", "language", "nationality", "title", "gender"]

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data["afas_employee_id"],
            "Employeenumber": "00000000" if data['sap_employee_id'] is None or data['sap_employee_id'] == '' else data['sap_employee_id'],
            "Startdate": data["start_date"],
            "Enddate": data["end_date"],
            "Actiontype": data["action"],
            "Reasonforaction": data["reason"],
            "Employmentstatus": data["employment_status"],
            "Companycode": data["company_code"],
            "Personnelarea": data["personal_area"],
            "Personnelsubarea": data["personal_sub_area"],
            "Employeegroup": data["employee_group"],
            "Employeesubgroup": data["employee_sub_group"],
            "OrgunitID": data["sap_org_unit_id"],
            "PositionID": data["position_id"],
            "Costcenter": data["cost_center"],
            "Salutation": data["salutation"],
            "Lastname": data["last_name"],
            "Firstname": data["first_name"],
            "Nameprefix": data["prefix"],
            "Secondnameprefix": data["second_name_prefix"],
            "NameatBirth": data["last_name"],
            "Initials": data["initials"],
            "Othertitle": data["other_title"],
            "Dateofbirth": data["date_of_birth"],
            "Communicationlanguage": data["language"],
            "Nationality": data["nationality"],
            "Title": data["title"],
            "Gender": data["gender"],
            "ExternalEmployeesubgroup": data['external_employee_subgroup']
        }

        # Update the request body with update fields
        response = self.base_class.post_data(uri='MasterActionPost/*', data=base_body, return_key='Employeenumber')
        return response

    def post_personal_data(self, data: dict, overload_fields: dict = None):
        """
        Upload the employee personal data
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['last_name', 'first_name', 'name_prefix', 'second_name_prefix', 'middle_name', 'middle_name', 'initials', 'second_title',
                          'date_of_birth', 'language', 'nationality', 'title', 'gender', 'name_at_birth']
        required_fields = ['afas_employee_id', 'sap_employee_id', 'start_date', 'end_date']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data["afas_employee_id"],
            "Employeenumber": data["sap_employee_id"],
            "Startdate": data["start_date"],
            "Enddate": data["end_date"]
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"Lastname": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"Firstname": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"Nameprefix": data['name_prefix']}) if 'name_prefix' in data else fields_to_update
        fields_to_update.update({"NameatBirth": data['name_at_birth']}) if 'name_at_birth' in data else fields_to_update
        fields_to_update.update({"Secondnameprefix": data['second_name_prefix']}) if 'second_name_prefix' in data else fields_to_update
        fields_to_update.update({"Middlename": data['middle_name']}) if 'middle_name' in data else fields_to_update
        fields_to_update.update({"Initials": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Salutation": data['salutation']}) if 'salutation' in data else fields_to_update
        fields_to_update.update({"Othertitle": data['second_title']}) if 'second_title' in data else fields_to_update
        fields_to_update.update({"Dateofbirth": data['date_of_birth']}) if 'date_of_birth' in data else fields_to_update
        fields_to_update.update({"Communicationlanguage": data['language']}) if 'language' in data else fields_to_update
        fields_to_update.update({"Nationality": data['nationality']}) if 'nationality' in data else fields_to_update
        fields_to_update.update({"Title": data['title']}) if 'title' in data else fields_to_update
        fields_to_update.update({"Gender": data['gender']}) if 'gender' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)
        response = self.base_class.post_data(uri='PersonalDataPost/*', data=base_body, return_key=None)
        return response

    def post_communication(self, data: dict, overload_fields: dict = None):
        """
        Post communication data to SAP like email or KID
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """

        allowed_fields = ['user_id', 'user_id_long']
        required_fields = ['afas_employee_id', 'sap_employee_id', 'start_date', 'end_date', 'user_type']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data["afas_employee_id"],
            "Employeenumber": data["sap_employee_id"],
            "Startdate": data["start_date"],
            "Enddate": data["end_date"],
            "Usertype": data["user_type"]
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"UserId": data['user_id']}) if 'user_id' in data else fields_to_update
        fields_to_update.update({"UserIdLong": data['user_id_long']}) if 'user_id_long' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='CommunicationPost/*', data=base_body, return_key='UserId')
        return response

    def post_organisational_unit(self, data: dict, overload_fields: dict = None):
        """
        Post OrgUnits to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = ['sap_organisational_unit_id', 'language']
        required_fields = ['start_date', 'end_date', 'organisational_unit_id', 'organisational_unit', 'parent_organisational_unit_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "OrgUnitID": "00000000" if data['sap_organisational_unit_id'] is None else data['sap_organisational_unit_id'],  # New organisational unit will have 00000000 as the OrgUnitID to indicate Creating new ones
            "Startdate": data["start_date"],
            "Enddate": data["end_date"],
            "Shorttext": data["organisational_unit_id"],
            "Longtext": data["organisational_unit"] if len(data['organisational_unit'])<=40 else data['organisational_unit'][:40], # SAP has a limit of 40 characters for longtext
            "OrgunitIDassigend": data["parent_organisational_unit_id"]
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"Langu": data['language']}) if 'language' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='OrgUnitPost/*', data=base_body, return_key='OrgUnitID')
        return response

    def post_position(self, data: dict, overload_fields: dict = None):
        """
        Post Position to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = ['sap_position_id', 'language', 'cost_center', 'is_manager']
        required_fields = ['start_date', 'end_date', 'job_code', 'job', 'sap_organisational_unit_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "PositionID": "00000000" if data['sap_position_id'] is None or data['sap_position_id'] == '' else data['sap_position_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "Shorttext": data['job_code'],
            "Longtext": data['job'] if len(data['job'])<=40 else data['job'][:40], # SAP has a limit of 40 characters for longtext
            "Omleader": False if data['is_manager'] is None or data['is_manager'] == '' else data['is_manager'],
            "OrgunitIDassigend": data['sap_organisational_unit_id']
        }

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"Langu": data['language']}) if 'language' in data else fields_to_update
        fields_to_update.update({"Costcenter": data['cost_center']}) if 'cost_center' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='PositionPost/*', data=base_body, return_key='PositionID')
        return response

    def post_workcenter(self, data: dict, overload_fields: dict = None):
        """
        Post Workcenters to SAP, assign to an existing position
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = []
        required_fields = ['workcenter_id', 'start_date', 'end_date', 'sap_position_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "WorkcenterID": data['workcenter_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "PositionID": data['sap_position_id'],
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='WorkcenterPost/*', data=base_body, return_key=None)
        return response

    def post_contract(self, data: dict, overload_fields: dict = None):
        """
        Post Contracts to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = ['entry_group_date']
        required_fields = ['afas_employee_id', 'sap_employee_id', 'start_date', 'end_date',
                           'contract_type', 'date_in_service', 'valid_until_date']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data['afas_employee_id'],
            "Employeenumber": "00000000" if data['sap_employee_id'] is None or data['sap_employee_id'] == '' else data['sap_employee_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "ContractType": data['contract_type'],
            "InitialEntryDate": data['date_in_service'],
            "VaildUntilDate": data['valid_until_date']
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"EntryGroupDate": data['entry_group_date']}) if 'entry_group_date' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='ContractElementPost/*', data=base_body, return_key=None)
        return response

    def post_additional_contract_element(self, data: dict, overload_fields: dict = None):
        """
        Post Contracts to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = ['leading_level']
        required_fields = ['afas_employee_id', 'sap_employee_id', 'start_date', 'end_date',
                           'start_date_leading_level', 'end_date_leading_level']
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data['afas_employee_id'],
            "Employeenumber": "00000000" if data['sap_employee_id'] is None or data['sap_employee_id'] == '' else data['sap_employee_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "LeadingLevelStartdate": data['start_date_leading_level'],
            "LeadingLevelEnddate": data['end_date_leading_level']
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"LeadingLevel": data['leading_level']}) if 'leading_level' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='AdditionalContractElementsPost/*', data=base_body, return_key=None)
        return response

    def post_basic_pay(self, data: dict, overload_fields: dict = None):
        """
        Post Basic Pay data, like capacity level and monthly hours, to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = []
        required_fields = ['afas_employee_id', 'sap_employee_id', 'start_date', 'end_date',
                           'hours_per_month', 'parttime_percentage']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data['afas_employee_id'],
            "Employeenumber": "00000000" if data['sap_employee_id'] is None or data['sap_employee_id'] == '' else data['sap_employee_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "WorkingHours": data['hours_per_month'],
            "CapUtilLvl": data['parttime_percentage']
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='BasicPaysPost/*', data=base_body, return_key=None)
        return response

    def post_matrix_manager(self, data: dict, overload_fields: dict = None):
        """
        Post Workcenters to SAP, assign to an existing position
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = []
        required_fields = ['matrix_manager_position_id', 'start_date', 'end_date', 'sap_position_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "ManagePositionID": data['matrix_manager_position_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "PositionID": data['sap_position_id'],
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='MatrixManagerPost/*', data=base_body, return_key=None)
        return response

    def post_power_of_attorney(self, data: dict, overload_fields: dict = None):
        """
        Post Power of Attorney to SAP
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :return: status code for request and optional error message
        """
        allowed_fields = []
        required_fields = ['afas_employee_id', 'start_date', 'end_date', 'power_of_attorney_code',
                           'company_code', 'value_limit', 'currency']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data['afas_employee_id'],
            "Startdate": data['start_date'],
            "Enddate": data['end_date'],
            "PowerOfAttorney": data['power_of_attorney_code'],
            "CompanyCode": data['company_code'],
            "LimitOfAmount": data['value_limit'],
            "Currency": data['currency']
        }
        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body.update(fields_to_update)

        response = self.base_class.post_data(uri='PowersAttorneyPost/*', data=base_body, return_key=None)
        return response

    def post_absence(self, data: dict):
        """
        Post Absence data to SAP
        :param data: Fields that are allowed are listed in allowed fields array.
        {
        "Afasemployeenumber" : "70913119",
        "Employeenumber" : "00000000",
        "Startdate" : "2022-01-01",
        "Enddate" : "2022-01-01",
        "AbsenceType" : "0200",
        "AbsenceHours" : "11.00"
        }
        """

        allowed_fields = []
        required_fields = ['employee_id', 'date_of_absence', 'type_of_hours_code', 'hours']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        base_body = {
            "Afasemployeenumber": data["employee_id"],
            "Employeenumber": "00000000",
            "Startdate": data["date_of_absence"],
            "Enddate": data["date_of_absence"],
            "AbsenceType": data["type_of_hours_code"],
            "AbsenceHours": data["hours"]
            }

        response = self.base_class.post_data(uri='AbsencePost/*', data=base_body)
        return response