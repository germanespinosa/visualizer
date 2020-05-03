import csv

def load(file):
    column_names = []
    rows = []
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                for cn in row:
                    column_names.append(cn.replace(" ",""))
                line_count += 1
            else:
                ci = 0
                nr = {}
                for c in row:
                    nr[column_names[ci]] = c
                    ci += 1
                if (ci == len(column_names)):
                    rows.append(nr)
                else:
                    print("error on file", file, "line", line_count)
                line_count += 1
    return {"column_names": column_names, "rows": rows}
