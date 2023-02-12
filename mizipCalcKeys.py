#!/usr/bin/env python
# This script is an implementation of lua code written by Iceman: 
# https://github.com/iceman1001/proxmark3/blob/master/client/scripts/calc_mizip.lua
# Thanks to him and y0no for this script:
# https://gist.github.com/y0no/70565a8d09203122181f3b3a08bffcbd

import sys

xortable = (
	('001', '09125a2589e5', 'F12C8453D821'),
	('002', 'AB75C937922F', '73E799FE3241'),
	('003', 'E27241AF2C09', 'AA4D137656AE'),
	('004', '317AB72F4490', 'B01327272DFD'),
)

def calcKey(uid, xorkey, keytype):
	p = []
	idx = {
		'A': (0,1,2,3,0,1),
		'B': (2,3,0,1,2,3),
	}.get(keytype)

	for i,j in enumerate(idx):
		p.append('%02x'% (uid[j] ^ xorkey[i]))

	return ''.join(p)

def hextostr(hexa):
	return bytes.fromhex(hexa)


def calc(UID):

	_uid = UID
	if len(_uid) != 8:
		print('Your UID has not the good length')
		sys.exit(1)

	try:
		uid = hextostr(_uid)

	except ValueError:
		print('Your UID is not a valid one')
		sys.exit(1)	


	ka = []
	kb = []
	ka.append('A0A1A2A3A4A5')
	kb.append('B4C132439EEF')
	for sec, xorA, xorB in xortable:
		keyA = calcKey(uid, hextostr(xorA), 'A')
		keyB = calcKey(uid, hextostr(xorB), 'B')
		ka.append(keyA.upper())
		kb.append(keyB.upper())

	keys = []
	keys.append(ka)
	keys.append(kb)
	return keys