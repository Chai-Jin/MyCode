#
# may be able to use as standalone, or as module.
#

# used when task is reattempting
import sys, os
import json
import shutil


##
# generate task, including task managing & json argument
# and run.
#
def generateTask(jobname, param='', keyword1=None, keyword2=None, key_type=None, custom_targets=None, **args):
	# create new task path and file
	workpath = os.path.join("WORK", jobname)
	createTask(workpath, keyword1, keyword2, key_type, custom_targets, **args)

	# managing state
	jobfn = jobname + ".json"	# useless?
	# remove DONE, ERROR file for clearing state
	def rmifex(p):
		if (os.path.exists(p)):
			os.remove(p)

	rmifex(os.path.join(workpath, "DONE"))
	rmifex(os.path.join(workpath, "ERROR"))

	# remove & generate job file for READY queue
	def mvifex(p, dest):
		if (os.path.exists(p)):
			os.rename(p, dest)

	if (workpath == None):
		raise Exception("workpath cannot be none")
	if (param == None):
		raise Exception("param cannot be none")
	if (key_type == None):
		key_type = "none"

	cmd = ['/bin/sh', './run_method_log.sh', workpath, param, key_type]

	rmifex(os.path.join("JOB", "OK", jobfn))
	rmifex(os.path.join("JOB", "FAIL", jobfn))
	with open(os.path.join("JOB", "READY", jobfn),'w') as f:
		json.dump({'cmd': cmd}, f)


##
# just create task json argument file
#
def createTask(workpath, keyword1=None, keyword2=None, key_type=None, custom_targets=None, **args):
# if new argument exists, then reset user_input.json
	user_input_path = os.path.join(workpath, "user_input.json")
	j = {}
	j['keyword1'] = ''
	j['keyword2'] = ''
	j['key_type'] = ''
	j['custom_targets'] = []
	if (os.path.exists(user_input_path)):
		with open(user_input_path, 'r') as f:
			j = json.load(f)
	if (keyword1 and keyword2 and key_type):
		j['keyword1'] = keyword1.strip()
		j['keyword2'] = keyword2.strip()
		j['key_type'] = key_type.strip()
	if (custom_targets):
		j['custom_targets'] = custom_targets
	for n,v in args.items():
		j[n] = v
	with open(user_input_path, "w") as f:
		json.dump(j, f)



def deleteTask(jobname):
	workpath = os.path.join("WORK", jobname)
	if (os.path.exists(workpath)):
		shutil.rmtree(workpath)



if __name__=='__main__':
	keyword1 = None
	keyword2 = None
	key_type = None
	if (len(sys.argv) > 3):
		keyword1 = sys.argv[3]
		keyword2 = sys.argv[4]
		key_type = sys.argv[5]
	generateTask(sys.argv[1], sys.argv[2], keyword1, keyword2, key_type)
