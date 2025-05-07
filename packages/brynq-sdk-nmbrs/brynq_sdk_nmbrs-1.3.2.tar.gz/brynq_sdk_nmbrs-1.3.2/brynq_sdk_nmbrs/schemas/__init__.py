"""Schema definitions for Nmbrs package"""

DATEFORMAT = '%Y%m%d'

from .address import AddressGet, AddressCreate, AddressUpdate, AddressDelete
from .bank import BankGet, BankCreate, BankUpdate, BankDelete
from .contracts import ContractGet, ContractCreate, ContractUpdate, ContractDelete
from .department import DepartmentGet, DepartmentCreate, DepartmentUpdate, DepartmentDelete
from .employees import EmployeeGet, EmployeeCreate, EmployeeUpdate, EmployeeDelete
from .employment import EmploymentGet, EmploymentCreate, EmploymentUpdate, EmploymentDelete
from .function import FunctionGet, FunctionCreate, FunctionUpdate, FunctionDelete
from .hours import FixedHoursGet, FixedHoursCreate, FixedHoursUpdate, HoursDelete, VariableHoursGet, VariableHoursCreate, VariableHoursUpdate
from .salary import SalaryGet, SalaryCreate, SalaryUpdate, SalaryDelete
from .wagecomponents import FixedWageComponentGet, FixedWageComponentCreate, FixedWageComponentUpdate, WageComponentDelete, VariableWageComponentGet, VariableWageComponentCreate, VariableWageComponentUpdate


__all__ = [
    'DATEFORMAT',
    'AddressGet', 'AddressCreate', 'AddressUpdate', 'AddressDelete',
    'BankGet', 'BankCreate', 'BankUpdate', 'BankDelete',
    'ContractGet', 'ContractCreate', 'ContractUpdate', 'ContractDelete',
    'DepartmentGet', 'DepartmentCreate', 'DepartmentUpdate', 'DepartmentDelete',
    'EmployeeGet', 'EmployeeCreate', 'EmployeeUpdate', 'EmployeeDelete',
    'EmploymentGet', 'EmploymentCreate', 'EmploymentUpdate', 'EmploymentDelete',
    'FunctionGet', 'FunctionCreate', 'FunctionUpdate', 'FunctionDelete',
    'FixedHoursGet', 'FixedHoursCreate', 'FixedHoursUpdate', 'HoursDelete',
    'VariableHoursGet', 'VariableHoursCreate', 'VariableHoursUpdate',
    'SalaryGet', 'SalaryCreate', 'SalaryUpdate', 'SalaryDelete',
    'FixedWageComponentGet', 'FixedWageComponentCreate', 'FixedWageComponentUpdate', 'WageComponentDelete',
    'VariableWageComponentGet', 'VariableWageComponentCreate', 'VariableWageComponentUpdate'
]
