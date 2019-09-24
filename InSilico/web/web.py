#!/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import random
from flask import Flask, request, render_template, jsonify, send_from_directory, url_for, redirect, jsonify
import datetime

import task
import api


BASEDIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
# app.config['UPLOAD_DIR'] = os.path.join(BASEDIR,'static/uploaded')
app.config['WORK_DIR'] = os.path.join(BASEDIR, 'WORK')
app.config['JOB_DIR'] = os.path.join(BASEDIR, 'JOB')

with open(os.path.join(BASEDIR, 'DATA/KEGG_pathway_list.txt')) as pathway:
	path_list = filter(lambda x: len(x), [s.upper().strip() for s in pathway.readlines()])

with open(os.path.join(BASEDIR, 'DATA/mouse_gene_list.txt')) as genes:
	gene_list = filter(lambda x: len(x), [s.upper().strip() for s in genes.readlines()])

@app.route("/")
def index():
	return render_template('index.html')


@app.route("/upload")
def upload():
	return render_template('upload.html', pathway=path_list)


@app.route("/genecheck")
def genecheck():
	keyword1 = request.args.get('keyword1').upper()
	print gene_list
	if keyword1 in gene_list:
		return 'This gene name is available.'
	else:
		return 'This gene name is NOT available.'


@app.route("/results")
def results():
	# just made temporarily; 
	# you should edit this function if you need to change 'results' page ...
	results = os.listdir(os.path.join(BASEDIR, 'WORK'))
	del results[0]		# to exclude .keep file; CAUTION: may be unstable
	return render_template('results.html', results=results)


@app.route("/help")
def help():
	return render_template('help.html')


# workid (may be null)
# keyword1(regulator gene)
# keyword2 / keyword_pathway(Hythesis or pathway)
# key_type(BEST or pathway)
# request.files['gene']
# request.files['mirna']
def submit_internal(form, files):
	# form parse
	keyword1 = form['keyword1']
	key_type = form['key_type']
	if (key_type == "BEST"):
		keyword2 = form['keyword2']
	else:
		keyword2 = form['keyword_pathway']

	# make workid
	# while True:
	#	  workid = "%06d" % random.randint(0, 100000)
	#	  curworkdir = os.path.join(app.config['WORK_DIR'], workid)
	#	  if os.path.isdir(curworkdir) == False:
	#		  break

	# make workid with datetime_msec
	if ('workid' not in form):
		workid = datetime.datetime.now().strftime('%Y%m%d%H%M%S_%f')
	else:
		workid = form['workid']

	# remove previous job if exist
	task.deleteTask(workid)

	# file upload
	curworkdir = os.path.join(app.config['WORK_DIR'], workid)
	os.mkdir(curworkdir)
	for key, f in files.iteritems():
		if f:
			filepath = os.path.join(curworkdir, f.filename)#key + '.txt')
			f.save(filepath)
			# files[key] = url_for('uploaded_file', workid=workid, filename=key + '.txt')
	
	# preprocess gene data (if csv, then comma replace)
	gene_fn = files['gene'].filename
	mirna_fn = files['mirna'].filename
	gene_fp = os.path.join(curworkdir, files['gene'].filename)
	mirna_fp = os.path.join(curworkdir, files['mirna'].filename)
	if (gene_fn[-4:] == '.csv'):
		with open(gene_fp,'r') as f:
			fdata = f.read()
			f.close()
		fdata = fdata.replace(',', '\t')
		with open(gene_fp[:-4]+'.txt','w') as f:
			f.write(fdata)
			f.close()
			gene_fn = gene_fn[:-4]+'.txt'
			gene_fp = gene_fp[:-4]+'.txt'
	if (mirna_fn[-4:] == '.csv'):
		with open(mirna_fp,'r') as f:
			fdata = f.read()
			f.close()
		fdata = fdata.replace(',', '\t')
		with open(mirna_fp[:-4]+'.txt','w') as f:
			f.write(fdata)
			f.close()
			mirna_fn = mirna_fn[:-4]+'.txt'
			mirna_fp = mirna_fp[:-4]+'.txt'

	# if no ctrl data, then generate it from data
	if ('gene_ctrl_rep' in form):
		rep_cnt = int(form['gene_ctrl_rep'])
		with open(gene_fp,'r') as f:
			genes = f.readline().split('\t')[1:]
			form['gene_ctrl'] = ','.join(genes[:rep_cnt])
	if ('mirna_ctrl_rep' in form):
		rep_cnt = int(form['mirna_ctrl_rep'])
		with open(mirna_fp,'r') as f:
			genes = f.readline().split('\t')[1:]
			form['mirna_ctrl'] = ','.join(genes[:rep_cnt])

	task.generateTask(workid, 'upload', keyword1, keyword2, key_type, [],
		genefn = gene_fn,
		mirnafn = mirna_fn,
		gene_ctrl = form['gene_ctrl'],
		mirna_ctrl = form['mirna_ctrl'],
		gene_type = form['gene_type'],
		mirna_type = form['mirna_type']
		)

	return workid


@app.route("/submit", methods=['POST'])
def submit():
	if request.method == 'POST':
		workid = submit_internal(request.form, request.files)
		return redirect(url_for('result', workid=workid))
	else:
		return "Invalid method"


@app.route('/retry/<workid>', methods=['POST'])
def retry(workid):
	mode = 'retry'
	if ("mode" in request.form):
		mode = request.form['mode']
	if ("keyword1" in request.form):
		keyword1 = request.form['keyword1']
		key_type = request.form['key_type']
		if (key_type == "BEST"):
			keyword2 = request.form['keyword2']
		else:
			keyword2 = request.form['keyword_pathway']
		task.generateTask(workid, mode, keyword1, keyword2, key_type)
	else:
		task.generateTask(workid, mode)
	return redirect(url_for('result', workid=workid))


@app.route('/retry_custom/<workid>', methods=['POST'])
def retry_custom(workid):
	# step_retry
	task.generateTask(workid, 'customtarget', None, None, None,
			request.form['custom_targets'].split(','))
	return redirect(url_for('result', workid=workid))


@app.route('/result/<workid>')
def result(workid):
	curworkdir = os.path.join(app.config['WORK_DIR'], workid)

	if os.path.exists(os.path.join(curworkdir, 'DONE')):
		fp = open(os.path.join(curworkdir, 'user_input.json'), 'r')
		userinput = json.load(fp)
		fp.close()

		# top100
		result_path = {}

		if os.path.exists(os.path.join(curworkdir, 'topPositive.txt')) == True:
			result_path['topPositive'] = url_for('download_file', workid=workid, filename='topPositive.txt')

		if os.path.exists(os.path.join(curworkdir, 'topPositiveNetwork.json.txt')):
			result_path['topPositiveNetwork'] = url_for('download_file', workid=workid, filename='topPositiveNetwork.json.txt')

		if os.path.exists(os.path.join(curworkdir, 'topNegative.txt')) == True:
			result_path['topNegative'] = url_for('download_file', workid=workid, filename='topNegative.txt')

		if os.path.exists(os.path.join(curworkdir, 'topNegativeNetwork.json.txt')):
			result_path['topNegativeNetwork'] = url_for('download_file', workid=workid, filename='topNegativeNetwork.json.txt')

		with open(os.path.join(curworkdir, 'result.json'),'r') as f:
			result = json.load(f)
		with open(os.path.join(curworkdir, 'topPositive.txt'),'r') as f:
			result['topPositive'] = map(lambda x: x.split('\t'), f.readlines())
		with open(os.path.join(curworkdir, 'topNegative.txt'),'r') as f:
			result['topNegative'] = map(lambda x: x.split('\t'), f.readlines())
		with open(os.path.join(curworkdir, 'topCustom.txt'),'r') as f:
			result['topCustom'] = map(lambda x: x.split('\t'), f.readlines())
		with open(os.path.join(curworkdir, 'best_gene.txt'),'r') as f:
			result['bestgenes'] = f.readlines()
		with open(os.path.join(curworkdir, 'filtered_gene.txt'),'r') as f:
			result['genevalues'] = map(lambda x: x.split('\t'), f.readlines()[:50])

		result['custom_targets'] = ','.join(map(lambda x: x[0], result['topCustom']))

		return render_template('result.html',
							   pathway=path_list,
							   workid=workid,
							   userinput=userinput,
							   result_path=result_path,
							   result=result
							   )
	elif os.path.exists(os.path.join(curworkdir, 'ERROR')):
		with open(os.path.join(curworkdir, 'ERROR'),'r') as f:
			message = f.read().strip()
		if (os.path.exists(os.path.join(curworkdir, 'log.txt'))):
			with open(os.path.join(curworkdir, 'log.txt'),'r') as f:
				log = f.read().strip()
		else:
			log = '(Log file does not exists)'
		with open(os.path.join(curworkdir, 'user_input.json'), 'r') as f:
			data = json.load(f)
		return render_template('result_error.html',
				workid=workid, log=log, message=message,
				data=data, pathway=path_list, userinput=data)
	else:
		return render_template('result_not_yet.html', workid=workid )

@app.route('/graph/<workid>')
def graph(workid):
	curworkdir = os.path.join(app.config['WORK_DIR'], workid)

	if not os.path.exists(os.path.join(curworkdir, 'DONE')):
		raise Exception('invalid path; working not done')
	else:
		return render_template('cyviewer.html',
								json_data_url='/graphjson/%s' % workid,
								workid=workid)
@app.route('/graph_old/<workid>')
def graph_old(workid):
	curworkdir = os.path.join(app.config['WORK_DIR'], workid)

	if not os.path.exists(os.path.join(curworkdir, 'DONE')):
		raise Exception('invalid path; working not done')
	else:
		return render_template('cyviewer_old.html',
								json_data_url='/graphjson/%s' % workid,
								workid=workid)

@app.route('/graphjson/<workid>')
def graphjson(workid):
	jsonfp = os.path.join(app.config['WORK_DIR'], workid, 'cydata.json')
	if not os.path.exists(jsonfp):
		return jsonify({})
	else:
		with open(jsonfp, 'r') as f:
			data = json.load(f)
		return jsonify(data)



@app.route('/download/<workid>/<filename>')
def download_file(workid, filename):
	return send_from_directory(os.path.join(app.config['WORK_DIR'], workid), filename)


@app.route('/api/job', methods=['POST'])
def api_create():
	if request.method != 'POST':
		return json.dumps({'code':0, 'message':'Invalid method'})
	job_id = request.form['id']
	# transform data
	files = {}
	files['gene'] = request.files['gene_exp']
	files['mirna'] = request.files['mirna_exp']
        # rename filename to csv, if none refered
        for key,x in request.files.items():
            if (x.filename.find('.') < 0):
                x.filename += '.csv'
        print [x.filename for key,x in request.files.items()]
        print request.form
	form = {}
	form['workid'] = request.form['id']
	form['keyword1'] = request.form['gene_name']
	form['keyword2'] = request.form['context']
	form['key_type'] = 'BEST'
	form['gene_ctrl_rep'] = request.form['num_re']
	form['mirna_ctrl_rep'] = request.form['num_re']
	form['gene_type'] = 'micro'
	form['mirna_type'] = 'micro'
	# run task and return
	submit_internal(form, files)
	return json.dumps({'code':1})

@app.route('/api/job/<workid>', methods=['GET', 'POST'])
def api_status(workid):
	job_id = workid
	job = api.GetJob(job_id)
	return json.dumps({'code':job.job_status, 'url':job.job_url})

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=9090, debug=True, threaded=True)
