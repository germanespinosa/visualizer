import sys
import os
import matplotlib
import log_file

matplotlib.use('TkAgg')

def get_file(folder, i):
    file_name = ("00" + str(i))[-3:] + "ms.log"
    file_path = folder + "/" + file_name
    if os.path.exists(file_path):
        return file_path
    else:
        return ""

if len(sys.argv) >= 2:
    if os.path.exists(str(sys.argv[1])):
        print('Source folder:', sys.argv[1])
    else:
        print('Source folder: ', sys.argv[1], "doesn't exists")
        exit(1)
else:
    print('No source folder specified.')
    exit(1)

source_folder = str(sys.argv[1])
results = {}
i = 1

for r, d, f in os.walk(source_folder):

    for file in f:
        if 'ms.log' in file:
            candidate = file.split(".")[0].replace("ms", "")
            if str.isdigit(candidate):
                ms = int(candidate)
                print(ms)
                results[ms] = log_file.load(source_folder + "/" + file)


# while get_file(source_folder, i) != "":
#     results[i] = load_file(get_file(source_folder, i))
#     i += 1
# i = 3
# while get_file(source_folder, i*5) != "":
#     results[i*5] = load_file(get_file(source_folder, i*5))
#     i += 1
#
# i = 6
# while get_file(source_folder, i*100) != "":
#     results[i*100] = load_file(get_file(source_folder, i*100))
#     i += 1


hs = []
ss = []
k = list(results.keys())
k.sort()
svalues={}
hvalues={}
for f in k:
    ssc = 0
    sfc = 0
    hsc = 0
    hfc = 0
    ssl = 0
    sfl = 0
    hsl = 0
    hfl = 0
    for r in results[f]["rows"]:
        if r["silver_result"] == "1":
            ssc += 1
            ssl += int(r["silver_len"])
        else:
            sfc += 1
            sfl += int(r["silver_len"])

        if r["habit_result"] == "1":
            hsc += 1
            hsl += int(r["habit_len"])
        else:
            hfc += 1
            hfl += int(r["habit_len"])
    hvalues[f] = hsc/(hsc+hfc)
    svalues[f] = ssc/(ssc+sfc)

    hs.append(hsc/(hsc+hfc))
    ss.append(ssc/(ssc+sfc))
    print(f, ssc/(ssc+sfc), hsc/(hsc+hfc))


datapoints = [1,100,1000,2000,3000,4000]
valuepoints1 = []
valuepoints2 = []
for dp in datapoints:
    valuepoints1.append(svalues[dp])
    valuepoints2.append(hvalues[dp])

matplotlib.pyplot.plot(datapoints, valuepoints1, "g" )

matplotlib.pyplot.show()
