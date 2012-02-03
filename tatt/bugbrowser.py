# -*- coding: utf-8 -*-
# Copyright 2011 Gentoo Foundation (Paweł Hajdan, Jr.)
#           2011 Thomas Kahle
# Distributed under the terms of the GNU General Public License v2

import curses.ascii
import itertools
import optparse
import os
import re
import subprocess
import sys
import textwrap
import xml.etree

import bugz.bugzilla
import portage.versions

import tatt.scriptwriter as scripts
import tatt.gentooPackage as gP

CPV_REGEX = re.compile("[A-Za-z0-9+_.-]+/[A-Za-z0-9+_-]+-[0-9]+(?:\.[0-9]+)*[a-z0-9_]*(?:-r[0-9]+)?")
repoman_dict = {}

def unicode_sanitize(text):
	"""Converts a possibly unicode text to a regular string."""
	if type(text) == unicode:
		real_output = text
	else:
		real_output = unicode(text, errors='replace')
	return real_output.encode("utf-8")

class TermTooSmall(Exception):
	pass

class Bug:
	def __init__(self, xml):
		self.__id = int(xml.find("bug_id").text)
		self.__summary = xml.find("short_desc").text
		self.__status = xml.find("bug_status").text
		self.__depends_on = [int(dep.text) for dep in xml.findall("dependson")]
		self.__comments = [c.find("who").text + "\n" + c.find("thetext").text for c in xml.findall("long_desc")]
		self.__cpvs_detected = False
		self.__cpvs = []
	
	def detect_cpvs(self):
		if self.__cpvs_detected:
			return
		for cpv_candidate in CPV_REGEX.findall(self.summary()):
			if portage.db["/"]["porttree"].dbapi.cpv_exists(cpv_candidate):
				self.__cpvs.append(cpv_candidate)
		self.__cpvs_detected = True
	
	def id_number(self):
		return self.__id
	
	def summary(self):
		return self.__summary
	
	def status(self):
		return self.__status
	
	def depends_on(self):
		return self.__depends_on
	
	def comments(self):
		return self.__comments
	
	def cpvs(self):
		assert(self.__cpvs_detected)
		return self.__cpvs

class BugQueue:
	def __init__(self):
		self.__bug_list = []
		self.__bug_set = set()
	
	def add_bug(self, bug):
		if self.has_bug(bug):
			return
		self.__bug_list.append(bug)
		self.__bug_set.add(bug.id_number())
	
	def has_bug(self, bug):
		return bug.id_number() in self.__bug_set
	
	def generate_stabilization_list(self):
		result = []
		for bug in self.__bug_list:
			result.append("# Bug %d: %s" % (bug.id_number(), bug.summary()))
			for cpv in bug.cpvs():
				result.append("=" + cpv)
		return "\n".join(result)

	def get_bugs(self):
		return self.__bug_list

# Main class (called with curses.wrapper later).
class MainWindow:
	def __init__(self, screen, bugs, bugs_dict, related_bugs, repoman_dict, bug_queue):
		self.bugs = bugs
		self.bugs_dict = bugs_dict
		self.related_bugs = related_bugs
		self.repoman_dict = repoman_dict
		self.bug_queue = bug_queue

		curses.curs_set(0)
		self.screen = screen

		curses.use_default_colors()
		self.init_screen()

		c = self.screen.getch()
		while c not in (ord("q"), curses.ascii.ESC):
			if c == ord("j"):
				self.scroll_bugs_pad(1)
			elif c == ord("k"):
				self.scroll_bugs_pad(-1)
			elif c == curses.KEY_DOWN:
				self.scroll_contents_pad(1)
			elif c == curses.KEY_UP:
				self.scroll_contents_pad(-1)
			elif c == curses.KEY_RESIZE:
				self.init_screen()
			elif c == ord("a"):
				self.add_bug_to_queue()

			c = self.screen.getch()

	def init_screen(self):
		(self.height, self.width) = self.screen.getmaxyx()

		if self.height < 12 or self.width < 80:
			raise TermTooSmall()

		self.screen.border()
		self.screen.vline(1, self.width / 3, curses.ACS_VLINE, self.height - 2)
		self.screen.refresh()

		self.fill_bugs_pad()
		self.refresh_bugs_pad()

		self.fill_contents_pad()
		self.refresh_contents_pad()

	def fill_bugs_pad(self):
		self.bugs_pad = curses.newpad(len(self.bugs),self.width)
		self.bugs_pad.erase()

		self.bugs_pad_pos = 0

		for i in range(len(self.bugs)):
			self.bugs_pad.addstr(i, 0,
				unicode_sanitize("    %d %s" % (self.bugs[i].id_number(), self.bugs[i].summary())))

	def scroll_bugs_pad(self, amount):
		height = len(self.bugs)

		self.bugs_pad_pos += amount
		if self.bugs_pad_pos < 0:
			self.bugs_pad_pos = 0
		if self.bugs_pad_pos >= height:
			self.bugs_pad_pos = height - 1
		self.refresh_bugs_pad()

		self.fill_contents_pad()
		self.refresh_contents_pad()

	def refresh_bugs_pad(self):
		(height, width) = self.bugs_pad.getmaxyx()
		for i in range(height):
			self.bugs_pad.addstr(i, 0, "   ")
			if self.bug_queue.has_bug(self.bugs[i]):
				self.bugs_pad.addch(i, 2, "+")
		self.bugs_pad.addch(self.bugs_pad_pos, 0, "*")
		pos = min(height - self.height + 2, max(0, self.bugs_pad_pos - (self.height / 2)))
		self.bugs_pad.refresh(
			pos, 0,
			1, 1,
			self.height - 2, self.width / 3 - 1)

	def fill_contents_pad(self):
		width = 2 * self.width / 3

		bug = self.bugs[self.bugs_pad_pos]

		output = []
		output += textwrap.wrap(bug.summary(), width=width-2)
		output.append("-" * (width - 2))

		cpvs = bug.cpvs()
		if cpvs:
			output += textwrap.wrap("Found package cpvs:", width=width-2)
			for cpv in cpvs:
				output += textwrap.wrap(cpv, width=width-2)
			output += textwrap.wrap("Press 'a' to add them to the stabilization queue.", width=width-2)
			output.append("-" * (width - 2))

		deps = [self.bugs_dict[dep_id] for dep_id in bug.depends_on()]
		if deps:
			output += textwrap.wrap("Depends on:", width=width-2)
			for dep in deps:
				desc = "%d %s %s" % (dep.id_number(), dep.status(), dep.summary())
				output += textwrap.wrap(desc, width=width-2)
			output.append("-" * (width - 2))
	
		related = self.related_bugs[bug.id_number()]
		if related:
			output += textwrap.wrap("Related bugs:", width=width-2)
			for related_bug in related:
				if str(related_bug['bugid']) == str(bug.id_number()):
					continue
				desc = related_bug['bugid'] + " " + related_bug['desc']
				output += textwrap.wrap(desc, width=width-2)
			output.append("-" * (width - 2))
	
		if bug.id_number() in repoman_dict and repoman_dict[bug.id_number()]:
			output += textwrap.wrap("Repoman output:", width=width-2)
			lines = repoman_dict[bug.id_number()].split("\n")
			for line in lines:
				output += textwrap.wrap(line, width=width-2)
			output.append("-" * (width - 2))
	
		for comment in bug.comments():
			for line in comment.split("\n"):
				output += textwrap.wrap(line, width=width-2)
			output.append("-" * (width - 2))

		self.contents_pad_length = len(output)

		self.contents_pad = curses.newpad(max(self.contents_pad_length, self.height), width)
		self.contents_pad.erase()

		self.contents_pad_pos = 0

		for i in range(len(output)):
			self.contents_pad.addstr(i, 0, unicode_sanitize(output[i]))

	def scroll_contents_pad(self, amount):
		height = self.contents_pad_length - self.height + 3

		self.contents_pad_pos += amount
		if self.contents_pad_pos < 0:
			self.contents_pad_pos = 0
		if self.contents_pad_pos >= height:
			self.contents_pad_pos = height - 1
		self.refresh_contents_pad()

	def refresh_contents_pad(self):
		self.contents_pad.refresh(
			self.contents_pad_pos, 0,
			1, self.width / 3 + 1,
			self.height - 2, self.width - 2)
		self.screen.refresh()
	
	def add_bug_to_queue(self):
		bug = self.bugs[self.bugs_pad_pos]

		# For now we only support auto-detected CPVs.
		if not bug.cpvs():
			return

		self.bug_queue.add_bug(bug)
		self.refresh_bugs_pad()

def launch_browser (config):
	# Launch the bug browser

	bug_queue = BugQueue()

	bugzilla = bugz.bugzilla.Bugz('http://bugs.gentoo.org', skip_auth=True)

	print "Searching for arch bugs..."
	raw_bugs = bugzilla.search("", cc="%s@gentoo.org" % config['arch'], keywords="STABLEREQ", status=None)
	bugs = [Bug(xml) for xml in bugzilla.get([bug['bugid'] for bug in raw_bugs]).findall("bug")]

	if not bugs:
		print 'The bug list is empty. Exiting.'
		sys.exit(0)

	dep_bug_ids = []

	bugs_dict = {}
	related_bugs = {}
	for bug in bugs:
		print "Processing bug %d: %s" % (bug.id_number(), bug.summary())
		bugs_dict[bug.id_number()] = bug
		related_bugs[bug.id_number()] = []
		repoman_dict[bug.id_number()] = ""
		bug.detect_cpvs()
		for cpv in bug.cpvs():
			pv = portage.versions.cpv_getkey(cpv)
			if config['verbose']:
				related_bugs[bug.id_number()] += bugzilla.search(pv, status=None)

			if config['repodir']:
				cvs_path = os.path.join(config['repodir'], pv)
				ebuild_name = portage.versions.catsplit(cpv)[1] + ".ebuild"
				ebuild_path = os.path.join(cvs_path, ebuild_name)
				manifest_path = os.path.join(cvs_path, 'Manifest')
				if os.path.exists(ebuild_path):
					original_contents = open(ebuild_path).read()
					manifest_contents = open(manifest_path).read()
					try:
						output = repoman_dict[bug.id_number()]
						output += subprocess.Popen(["ekeyword", config['arch'], ebuild_name], cwd=cvs_path, stdout=subprocess.PIPE).communicate()[0]
						subprocess.check_call(["repoman", "manifest"], cwd=cvs_path)
						output += subprocess.Popen(["repoman", "full"], cwd=cvs_path, stdout=subprocess.PIPE).communicate()[0]
						repoman_dict[bug.id_number()] = output
					finally:
						f = open(ebuild_path, "w")
						f.write(original_contents)
						f.close()
						f = open(manifest_path, "w")
						f.write(manifest_contents)
						f.close()
			else:
				print "repodir not configured, skipping repoman output generation"
				
		dep_bug_ids += bug.depends_on()

	dep_bug_ids = list(set(dep_bug_ids))
	dep_bugs = [Bug(xml) for xml in bugzilla.get(dep_bug_ids).findall("bug")]
	for bug in dep_bugs:
		bugs_dict[bug.id_number()] = bug

	try:
		curses.wrapper(MainWindow, bugs=bugs, bugs_dict=bugs_dict, related_bugs=related_bugs, repoman_dict=repoman_dict, bug_queue=bug_queue)
	except TermTooSmall:
		print "Your terminal window is too small, please try to enlarge it"
		sys.exit(1)
	
	stabilization_list = bug_queue.generate_stabilization_list()
	if stabilization_list:
		with open(config['unmaskfile'], "w") as f:
			f.write(stabilization_list)
			print "Writing stabilization list to %s" % config['unmaskfile']

	for b in bug_queue.get_bugs():
		packages = [gP.gentooPackage(s) for s in b.cpvs()]
		jobname = packages[0].packageName()
		scripts.writeusecombiscript(jobname, packages, config)
		scripts.writerdepscript (jobname, packages, config)
		scripts.writecommitscript (jobname, str(b.id_number()), packages, config)
		scripts.writeCleanUpScript (jobname, config)
