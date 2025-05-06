import os
import chelt_plan
from mysqlquerys import connect, mysql_rm
import datetime as dt
from datetime import date, datetime
import time
import numpy as np

compName = os.getenv('COMPUTERNAME')

def get_cheltuieli(ini_file, selectedStartDate, selectedEndDate):
    app = chelt_plan.CheltuieliPlanificate(ini_file)
    app.prepareTablePlan('all', selectedStartDate.date(), selectedEndDate.date())
    # app.prepareTablePlan('Siri&Radu', selectedStartDate.date(), selectedEndDate.date())
    for i in app.expenses:
        print(i)
    # print(app.tot_val_of_monthly_expenses())
    # print(app.tot_val_of_expenses())
    # print(app.tot_val_of_irregular_expenses())


def add_to_one_time_transactions(ini_file):
    app = chelt_plan.CheltuieliPlanificate(ini_file)
    name = 'Zbor ai mei Salzburg'
    value = 91.98
    myconto = 'Siri&Radu'
    pay_day = datetime(2024, 6, 17)
    app.add_one_time_transactions(name, value, myconto, pay_day)

    # app.prepareTablePlan('all', selectedStartDate.date(), selectedEndDate.date())
    # for i in app.expenses:
    #     print(i)
    # print(app.tot_val_of_monthly_expenses())
    # print(app.tot_val_of_expenses())
    # print(app.tot_val_of_irregular_expenses())


def get_income(ini_file, selectedStartDate, selectedEndDate):
    income = chelt_plan.Income(ini_file)
    income.prepareTablePlan('all', selectedStartDate.date(), selectedEndDate.date())
    # print(20*'#')
    # print(income.tableHead)
    for i in income.income:
        print(i)
    # print(income.netto)
    # print(income.monthly_income)
    # print(income.irregular_income)


def get_totals(ini_file, conto, dataFrom, dataBis):
    ch = chelt_plan.CheltPlusIncome(ini_file, conto, dataFrom, dataBis)
    print(ch.summary_table)


# def get_program(ini_file, selectedStartDate, selectedEndDate):
#     program = kalendar.Kalendar(ini_file)
#     # print(program.default_interval)
#     appointments = program.get_appointments_in_interval('all', selectedStartDate, selectedEndDate)
#     for i in appointments:
#         print(i)

def prep_yearly_graf(ini_file):
    app_plan = chelt_plan.CheltuieliPlanificate(ini_file)
    months = [dt.date(2000, m, 1).strftime('%B') for m in range(1, 13)]
    # print(app_plan.myContos)
    # monthly_dict = {}
    for month in months:
        print(month)
        all_contos_monthly_tot_val_of_expenses = 0
        all_contos_monthly_tot_val_of_monthly_expenses = 0
        all_contos_monthly_tot_val_of_irregular_expenses = 0
        for currentConto in app_plan.myContos:
            print('\t',currentConto)
            selectedStartDate, selectedEndDate = (chelt_plan.get_monthly_interval(month, datetime.now().year))
            app_plan.prepareTablePlan(currentConto, selectedStartDate, selectedEndDate, hideintercontotrans=True)
            print('\t\t','tot_val_of_expenses', app_plan.tot_val_of_expenses)
            print('\t\t','tot_val_of_monthly_expenses', app_plan.tot_val_of_monthly_expenses)
            print('\t\t','tot_val_of_irregular_expenses', app_plan.tot_val_of_irregular_expenses)
            all_contos_monthly_tot_val_of_expenses += app_plan.tot_val_of_expenses
            all_contos_monthly_tot_val_of_monthly_expenses += app_plan.tot_val_of_monthly_expenses
            all_contos_monthly_tot_val_of_irregular_expenses += app_plan.tot_val_of_irregular_expenses
        print('\t','all')
        print('\t\t', 'tot_val_of_expenses', all_contos_monthly_tot_val_of_expenses)
        print('\t\t', 'tot_val_of_monthly_expenses', all_contos_monthly_tot_val_of_monthly_expenses)
        print('\t\t', 'tot_val_of_irregular_expenses', all_contos_monthly_tot_val_of_irregular_expenses)


def main():
    script_start_time = time.time()
    selectedStartDate = datetime(2025, 1, 1, 0, 0, 0)
    selectedEndDate = datetime(2025, 1, 31, 0, 0, 0)

    if compName == 'DESKTOP-5HHINGF':
        ini_file = r"D:\Python\MySQL\cheltuieli.ini"
    else:
        ini_file = r"C:\_Development\Diverse\pypi\cfgm.ini"
        # ini_file = r"C:\_Development\Diverse\pypi\cfgmRN.ini"

    # prep_yearly_graf(ini_file)
    # return

    # get_cheltuieli(ini_file, selectedStartDate, selectedEndDate)

    # return

    # user = chelt_plan.Users(None, ini_file)
    # user.erase_traces()
    # return
    # user = chelt_plan.Users('radu', ini_file)
    # zz = r"C:\_Development\Diverse\pypi\radu\cheltuieli\src\cheltuieli\static\backup_profile\000000001\2025_01_23__08_53_47_000000001.zip"
    # user.import_profile_with_files(zz, import_files=True)
####################################################
    # currentConto = 'EC'
    # currentConto = 'Siri&Radu'
    currentConto = 'all'
    currentConto = 'DeutscheBank'
    # currentConto = 'N26'
    # currentConto = 'N26 Family Mircea'
    # app_plan = chelt_plan.CheltuieliPlanificate(ini_file)
    # # print(app_plan.get_all_sql_vals())
    # payments_dict, labels = app_plan.prep_yearly_graf()
    # print(labels)
    # for k, v in payments_dict.items():
    #     print(k, v)
    # print(table.shape)
    # app_plan.prepareTablePlan(currentConto, selectedStartDate.date(), selectedEndDate.date(), hideintercontotrans=True)
    # print(app_plan.expenses.shape)
    # for ii in app_plan.expenses:
    #     print(ii)
    # print(app_plan.tableHead)
    # for ii in app_plan.income:
    #     print('ÜÜ', ii)
    # print(app_plan.tableHead)
    # print('tot_no_of_irregular_expenses', app_plan.tot_no_of_irregular_expenses)
    # print('tot_val_of_irregular_expenses', app_plan.tot_val_of_irregular_expenses)
    # print('tot_no_of_monthly_expenses', app_plan.tot_no_of_monthly_expenses)
    # print('tot_val_of_monthly_expenses', app_plan.tot_val_of_monthly_expenses)
    # print('tot_val_of_expenses', app_plan.tot_val_of_expenses)
    # print('tot_no_of_expenses', app_plan.tot_no_of_expenses)
    # print('tot_no_of_income', app_plan.tot_no_of_income)
    # print('tot_val_of_income', app_plan.tot_val_of_income)
    # print('tot_no_of_expenses_income', app_plan.tot_no_of_expenses_income)
    # print('tot_val_of_expenses_income', app_plan.tot_val_of_expenses_income)
    # return
####################################################

    # hideintercontotrans = True
    # chelt_app = chelt_plan.CheltPlanVSReal(ini_file, currentConto, selectedStartDate.date(), selectedEndDate.date(), hideintercontotrans)
    # chelt_app.find_planned_in_real_expenses_table(hideintercontotrans, 15)
    # chelt_app.find_unplanned_real_expenses(hideintercontotrans, 15)
    # for i in chelt_app.found_payments_from_planned:
    #     print(i)
    # print(100*'Ö')
    # for i in chelt_app.found_payments_from_planned_display_table:
    #     print(i)
    # print(100 * 'Ö')
    # chelt_app.find_unplanned_real_expenses(hideintercontotrans, 15)
    # for rr in chelt_app.unplanned_myconto_dict['EC']:
    #     print(rr)
    # print(chelt_app.sum_planned)
    # print(chelt_app.sum_realised)
    # print(chelt_app.sum_realised_from_planned_found)
    # print(chelt_app.sum_realised_from_not_found_payments_from_planned)
    # print(chelt_app.sum_of_unplanned_real_expenses)
    # print(chelt_app.realised_from_planned_found_in_interval)
    # print(chelt_app.sum_realised_from_planned_found_in_interval)
    # for i in chelt_app.unplanned_real_expenses:
    #     print(i)
    # print(100*'*')
    # print(type(unplanned_real_expenses), unplanned_real_expenses.shape)
    # print(chelt_app.sum_planned)
    # print(chelt_app.no_of_transactions_planned)
    # print(chelt_app.sum_realised_from_planned_found)
    # print(chelt_app.sum_planned_from_planned_found)
    # print(chelt_app.unplanned_real_expenses_without_N26)
    # print(chelt_app.unplanned_real_expenses_only_N26)
    # for i in chelt_app.expenses:
    #     print(i)

################################################################################

    app_reale = chelt_plan.CheltuieliReale(ini_file)
    csv = r"D:\Documente\Radu\Banken\DeutschBank\export_csv\Transactions_220_552695900_20250227_164747.csv"
    # app_reale.import_CSV_new(currentConto, csv)
    # app_reale.find_chelt_plan_rows_in_banks_tables_and_write_to_plan_vs_real_table()
    # app_reale.find_knowntrans_in_banks_tables_and_write_to_plan_vs_real_table()
    # print(app_reale.get_rows_from_chelt_plan_that_misses_in_banks())
    # print(app_reale.check_1_row_from_chelt_plan(row_id=170, write_in_real_table=True))
    # todo aici am ramas
    # print(100 * '-')
    # app_reale.prepareTableReal_new(currentConto, selectedStartDate, selectedEndDate, True)
    # for rex in app_reale.realIncome:
    #     print(rex)
    # print(100*'+')
    # print(app_reale.tot_no_of_expenses)
    # print(app_reale.table_head)
    # print(app_reale.tot_val_of_expenses)
    # # print(app_reale.tot_no_of_expenses())

    # not_found = app_reale.get_rows_from_chelt_plan_that_misses_in_banks()
    # for ii in not_found:
    #     print(ii)

    scrip_end_time = time.time()
    duration = scrip_end_time - script_start_time
    duration = time.strftime("%H:%M:%S", time.gmtime(duration))
    print('run time: {}'.format(duration))


if __name__ == '__main__':
    main()
