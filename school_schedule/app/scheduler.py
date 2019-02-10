import pandas as pd
from pulp import *
import numpy as np
import re
from django.http import HttpResponse
from io import BytesIO as IO
import os


def create_schedule(file_path):
    ## DATA PREPROCESSING ##
    dfs = pd.read_excel(file_path, sheet_name=None, index_col=0)

    # get rid of the file no that it's in memory
    os.remove(file_path)

    # get easier to access copy of availability
    av = dfs['Availabilities']

    # mark availabilities with 1 and all else with 0
    av = av.fillna(0)
    av = av.replace('x', 1)

    # turn columns to strings so we can query with them
    av.columns = [str(col) for col in av.columns]

    # get easier to access copy of requirements
    req = dfs['Requirements']

    # mark mark blank quantities as 0
    req = req.fillna(0)

    # make a list of input cols/index so we can make new indices with them
    meetings = dict(enumerate(av.index))
    times = dict(enumerate(av.columns))

    ## BUILD AND RUN MODEL ##
    # Create a variable, "prob", to contain our problem data
    prob = LpProblem("schedule_meetings", LpMinimize)

    # Create problem variables
    # if meeting i takes place at time j
    x = LpVariable.dicts('x', (meetings.keys(), times.keys()), lowBound=0,
                         upBound=1, cat='Integer')

    # 1
    # Objective is to minimize total meetings
    prob += lpSum(lpSum(x[i][j] for i in meetings) for j in times)

    # 2
    # Each meeting must occur at a time that meeting is available to occur
    for i in meetings:
        for j in times:
            prob += x[i][j] <= av.loc[meetings[i], times[j]], ''

    # 3
    # Each meeting must occur the required amount of times
    for i in meetings:
        prob += lpSum(x[i][j] for j in times) == req.loc[meetings[i], 'Quantity'], ''

    # 4
    # At most one meeting can happen at a time
    for j in times:
        prob += lpSum(x[i][j] for i in meetings) <= 1, ''

    # The problem data is written to an lp file
    prob.writeLP('schedule_meetings.lp')

    # The problem is solved using PuLP's choice of Solver
    prob.solve()

    # save results to dictionary for easy access later
    results = {
        'status': LpStatus[prob.status],
        'objective': value(prob.objective),
        'variables': prob.variables()
    }

    # trigger error if non-optimal
    if results['status'] != 'Optimal':
        return 'Failed'

    ## DATA POSTPROCESSING ##
    # capture the meeting and the time in each variable
    regex = re.compile('x_(.*)_(.*)')

    # create blank df with same cols and index as av to fill with solution
    sol = av.copy()
    sol = sol.replace(sol, np.nan)

    for v in results['variables']:
        # if given meeting happens at given time
        if v.varValue > 0:
            m = regex.search(v.name)
            # mark it down in the solution df
            sol.loc[meetings[int(m.group(1))], times[int(m.group(2))]] = 'x'

    # add solution to our df dict
    dfs['Solution'] = sol

    ## SAVING TO IO ##
    excel_file = IO()

    # specify where to save and what engine to use
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

    # write each sheet to the workbook
    for sheet, df in dfs.items():
        df.to_excel(writer, sheet)

    # save the workbook to io and close it
    writer.save()
    writer.close()

    # reset the read position to 0 and return everything after it
    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=output.xlsx'

    return response


if __name__ == '__main__':
    file_path = 'C:\\Users\\seanp\\Documents\\personal_projects\\school_schedule\\school_schedule\\media\\data_model.xlsx'
    create_schedule(file_path=file_path)
