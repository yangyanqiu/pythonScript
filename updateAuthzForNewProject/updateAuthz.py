#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import configparser
import sys
import shutil
import os

#reload optionxform
class NewConfigParser(configparser.ConfigParser):
	def optionxform(self,optionstr):
		return optionstr

#get old groups
def getGroups(project):
	configfile = "./%s/conf/authz"%project
	cf = NewConfigParser()
	cf.read(configfile)
	groups = cf.options("groups")
	return groups

#make new group name for new project
def newGroups(project,groups):
	newgroups = []

	for group in groups:
		newgroupname = "%s_%s"%(project,group)
		newgroups.append(newgroupname)
	#print(newgroups)
	return newgroups

#make new authz for new project
def newConfigFile(project):
	config_path = "./%s/conf/authz"%project
	new_config_path = "./%s/conf/authz_new"%project
	back_config_path = "./%s/conf/authz_back"%project
	#backup config file
	shutil.copyfile(config_path, back_config_path)

	groups = getGroups(project)

	with open(config_path, 'r') as fr, open(new_config_path, 'w') as fw:
		for line in fr:
			for group in groups:
				new_group_name = "%s_%s"%(project,group)
				line = line.replace(group, new_group_name)
			if "[project" in line:
				line = line.replace("project", project)	
			fw.write(line)
	
	shutil.copyfile(new_config_path, config_path)
	os.remove(new_config_path)

#update public authz file with new project authz
def updatePublicAuthzFile(project, file_path):
	project_authz = "./%s/conf/authz"%project
	public_authz = file_path+"/authz"
	backfile = file_path+"/authz_back"
	new_public_authz = file_path+"/authz_new"
	
        #backup config file
	shutil.copyfile(public_authz, backfile)

	
	project_groups = []
	project_authzs = []	
	
	with open(public_authz, 'r') as fr:
		temp = 0
		for line in fr.readlines():
			if "[/]" not in line and temp == 0:
				project_groups.append(line)
			elif "[/]" in line and temp == 0:
				temp = 1
				project_authzs.append(line)
			elif temp == 1:
				project_authzs.append(line)

	#print("-------------[%s"%project)
	with open(project_authz,'r') as fr:
		group_or_authz = 0
		for line in fr.readlines():
			if group_or_authz == 0 and "[groups]" in line and "#" not in line:
				group_or_authz = 1
			elif group_or_authz == 1 and "[%s"%project not in line:
				project_groups.append(line)
			elif group_or_authz == 1 and "[%s"%project in line:
				group_or_authz = 2
				project_authzs.append(line)
			elif group_or_authz == 2:
				project_authzs.append(line)
		#print("project_group:\n%s\nproject_authz:\n%s"%(project_groups,project_authzs))

	#write in public authz file
	with open(new_public_authz, 'w') as fw:
		for line in project_groups:
			fw.write(line)
		for line in project_authzs:
			fw.write(line)

	shutil.copyfile(new_public_authz, public_authz)
	os.remove(new_public_authz)
	print("update authz file successfully!")

if __name__ == '__main__':
	project = ''
	try:

		project = sys.argv[1]
		file_path = sys.argv[2]
		#delete the right / when the end of path is /
		file_path = file_path.rstrip('/')
	except Exception as e:
		print("Error!!!\nMust have 2 parameters when excute this script:\n    1. The first para is project name\n    2. The second para is public authz path without / at the end~\nfor example:\n %s newProject /home/svn"%(sys.argv[0]))
		exit(-1)	
	
	#make new project authz file
	newConfigFile(project)

	#update public authz file with new project authz file
	updatePublicAuthzFile(project,file_path)
