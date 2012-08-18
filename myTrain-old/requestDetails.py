import requests
import re

r = requests.post('http://www.cp.pt/cp/searchTimetableFromRightTool.do',params={'departStation': 'santa apolonia', 'arrivalStation':'oriente', 'goingDate':'2012-07-02', 'goingTime':'','returningDate':'','returningTime':'','ok':'OK'})

m = re.findall('toggleLine\((\d+),(\d+)\)', r.content)

p = m[0]
#for p in m:
r2 = requests.post('http://www.cp.pt/cp/detailSolution.do', cookies=r.cookies, params={'page': p[1], 'selectedSolution': p[0], 'solutionType':'selectedSolution'})
print r2.content