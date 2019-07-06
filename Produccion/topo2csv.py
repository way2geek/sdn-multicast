import csv
import json

PATH_TOPO = "./topologias/topo_anillo_simple.json"

infile = open(PATH_TOPO,"r")
outfile = open ("topo_convertida.csv", "w")

writer = csv.writer(outfile)

for row in json.loads(infile.read()):
	writer.writerow(row)

