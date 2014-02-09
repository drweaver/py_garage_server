import sqlite3
import logging
import sys
from time import time, gmtime, strftime

logger = logging.getLogger("garage_dao")

class GarageDao():

	_GARAGE_CREATE_SQL="CREATE TABLE IF NOT EXISTS garage_audit (id INTEGER PRIMARY KEY AUTOINCREMENT, reason TEXT NOT NULL, state TEXT NOT NULL, time INTEGER NOT NULL)"
	_GARAGE_INSERT_SQL="INSERT INTO garage_audit (reason,state,time) values (?,?,?)"
	_GARAGE_GET_LAST_STATE_SQL="SELECT state FROM garage_audit ORDER BY time DESC LIMIT 1"
	_GARAGE_GET_LAST_CLOSED_SQL="SELECT state, time FROM garage_audit ORDER BY time DESC"
	_GARAGE_AUDIT_HISTORY_SQL="SELECT id,reason,state,time FROM garage_audit ORDER BY time ASC"

	def __init__(self,db_file='/var/tmp/garage.db'):
		self._db_file=db_file
		self._open()
		self._db.execute(GarageDao._GARAGE_CREATE_SQL)
		self._commit_and_close()

	def _open(self):
		self._conn = sqlite3.connect(self._db_file)
		self._db = self._conn.cursor()
	
	def _close(self):
		self._conn.close()

	def _commit(self):
		self._conn.commit()

	def _commit_and_close(self):
		self._commit()
		self._close()

	def update_status(self, reason, state, update_time=None):
		self._open()
		if update_time is None: update_time = time()
		self._db.execute(GarageDao._GARAGE_INSERT_SQL, (reason,state,update_time))
		self._commit_and_close()
		
	def door_status(self):
		self._open()
		row = self._db.execute(GarageDao._GARAGE_GET_LAST_STATE_SQL).fetchone()
		self._close()
		if row:
			return row[0]
		return None

	def last_state_transition_from(self, state):
		"""
		Returns 0 if no transition is found.
		Returns None if currently in that state.
		"""
		self._open()
		query = self._db.execute(GarageDao._GARAGE_GET_LAST_CLOSED_SQL)
		t = None

		while 1:
			row = query.fetchone()
			if not row:
				self._close()
				return 0
			if row[0] == state:
				self._close()
				return t
			t = row[1]

	def audit_history(self,file, date_format='%c'):
		self._open()
		query = self._db.execute(GarageDao._GARAGE_AUDIT_HISTORY_SQL)
		while 1:
			row = query.fetchone()
			if not row: break
			file.write("|")
			for c in (0, 1, 2):
				file.write(str(row[c])+"|")
			file.write(strftime(date_format,gmtime(row[3]))+"|")
			file.write("\n")
		self._close()

if __name__ == '__main__':
	dao = GarageDao()
	dao.audit_history(sys.stdout)
	