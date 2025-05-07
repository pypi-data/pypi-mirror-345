from .base_functions import BaseFunctions
import requests


class DelimitEndpoints:
    def __init__(self, label: str, data_dir: str, certificate_file: str = None, key_file: str = None, debug: bool = False):
        self.base_class = BaseFunctions(label=label, data_dir=data_dir, certificate_file=certificate_file, key_file=key_file, debug=debug)
        self.data_dir = data_dir
        self.debug = debug

    def delimit_master_action(self, employee_id, start_date, end_date, action_type, reason_for_action):
        """
        Delimit personal data
        :param employee_id: the ID of the employee you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{end_date}',Enddate='9999-12-31',Actiontype='{action_type}',Reasonforaction='{reason_for_action}'"    # Masteraction delimit is picking the enddate as the startdate for the termination, no need to use the original startdate of the record
        response = self.base_class.delete_data(uri='MasterActionDel', filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_org_unit(self, org_unit, start_date, end_date):
        """
        Delimit organisational units
        :param org_unit: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :return: status
        """
        data_filter = f"OrgUnitID='{org_unit}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri='OrgUnitDel', filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_position(self, position_id, start_date, end_date):
        """
        Delimit positions in SAP
        :param position_id: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :return: status
        """
        data_filter = f"PositionID='{position_id}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri="PositionDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delete_workcenter(self, position_id, start_date, end_date, workcenter):
        """
        Delimit positions in SAP
        :param position_id: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :param workcenter: the workcenter you want to delimit
        :return: status
        """
        data_filter = f"PositionID='{position_id}',Startdate='{start_date}',Enddate='{end_date}',WorkcenterID='{workcenter}'"
        response = self.base_class.delete_data(uri="WorkcenterDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delete_matrix_manager(self, position_id, start_date, end_date, matrix_manager_position_id):
        """
        Delimit positions in SAP
        :param position_id: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :param matrix_manager_position_id: the matrix_manager_position you want to delimit
        :return: status
        """
        data_filter = f"PositionID='{position_id}',Startdate='{start_date}',Enddate='{end_date}',ManagePositionID='{matrix_manager_position_id}'"
        response = self.base_class.delete_data(uri="MatrixManagerDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_contract(self, employee_id, start_date, end_date):
        """
        Delimit positions in SAP
        :param position_id: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :param workcenter: the workcenter you want to delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri="ContractElementDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_additional_contract_element(self, employee_id, start_date, end_date):
        """
        Delimit positions in SAP
        :param position_id: the ID of the organisational unit you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :param workcenter: the workcenter you want to delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri="AdditionalContractElementDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_basic_pay(self, employee_id, start_date, end_date):
        """
        Delimit the Basic Pay in SAP
        :param employee_id: the AFAS Employee ID you want to delimit
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri="BasicPayDel", filter=data_filter)
        response.raise_for_status()
        return response

    def delimit_power_of_attorney(self, employee_id, start_date, end_date, power_of_attorney_code, company_code):
        """
        Delimit power of attorney in SAP
        :param employee_id: the AFAS ID of the employee in case
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :param power_of_attorney_code: the code of the power of attorney you want to delimit
        :param company_code: the company code of the power of attorney you want to delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{start_date}',Enddate='{end_date}',PowerOfAttorney='{power_of_attorney_code}',CompanyCode='{company_code}'"
        response = self.base_class.delete_data(uri="PowersAttorneyDel", filter=data_filter)
        response.raise_for_status()
        return response


    def delimit_absence(self, employee_id, start_date, end_date):
        """
        Delimit absence record in SAP
        :param employee_id: the AFAS ID of the employee in case
        :param start_date: the start date of the record you want to delimit
        :param end_date: the end date at which the record will be delimit
        :return: status
        """
        data_filter = f"Afasemployeenumber='{employee_id}',Startdate='{start_date}',Enddate='{end_date}'"
        response = self.base_class.delete_data(uri="AbsenceDel", filter=data_filter)
        response.raise_for_status()
        return response