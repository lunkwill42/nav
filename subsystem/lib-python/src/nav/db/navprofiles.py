# -*- coding: ISO8859-1 -*-
# Copyright 2003, 2004 Norwegian University of Science and Technology
#
# This file is part of Network Administration Visualized (NAV)
#
# NAV is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# NAV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAV; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
# Authors: Morten Vold <morten.vold@itea.ntnu.no>
#
"""
This module extends the database abstraction generated by forgetSQL
for the navprofiles database, and adds a lot of useful functionality
to the Account system.
"""
import nav.db
from nav.db.forgotten.navprofiles import *
import nav.pwhash
import md5

class Account(nav.db.forgotten.navprofiles.Account):
    def getGroups(self):
        """
        Return a list of Accountgroup objects this Account is a member of.
        """
        links = self.getChildren(Accountingroup)
        return [Accountgroup(link.group) for link in links]

    def getOrgIds(self):
        """
        Returns a list of organization ids this Account is associated with.
        """
        links = self.getChildren(Accountorg)
        return [link.orgid for link in links]

    def getImplicitOrgIds(self):
        """
        Returns a list of  organization ids this Account is associated
        with,  including   implicit  organization  membersships.   The
        hierarchy of  organizations from manage is  taken into account
        here.
        """
        conn = nav.db.getConnection('webfront', 'manage')

        # First, get the organizational units this user is an explicit
        # member of.
        orgList = self.getOrgIds()

        if len(orgList) > 0:
            # Then we need to trace organizational units below these in the
            # hierarchy.
            manageCursor = conn.cursor()
            done = False
            while not done:
                orgString = ",".join(["'%s'" % org for org in orgList])
                sql = \
                    """
                    SELECT DISTINCT orgid
                    FROM org
                    WHERE parent IN (%s)
                    AND orgid NOT IN (%s);
                    """ % (orgString, orgString)
                manageCursor.execute(sql)
                if manageCursor.rowcount < 1:
                    done = True
                else:
                    orgList.extend([row[0] for row in manageCursor.fetchall()])

        return orgList


    def loadByLogin(cls, login):
        """
        Load and return an Account object by login name instead of id number.
        """
        result = Account.getAll(where="login=%s" % nav.db.escape(login))
        if len(result) < 1:
            raise NoSuchAccountError, login
        else:
            return result[0]

    # Make sure loadByLogin becomes a class method
    loadByLogin = classmethod(loadByLogin)

    def authenticate(self, password):
        """
        Return True if the submitted authentication tokens are valid
        for this Account.  In simpler terms; when password
        authentication is used, this method compares the given
        password with the one stored for this account and returns true
        if they are equal.  If the stored password is blank, we
        interpret this as: 'The user is not allowed to log in'

        In the future, this could be extended to accept other types of
        authentication tokens, such as personal certificates or
        whatever.
        """
        if len(self.password.strip()) > 0:
            stored_hash = nav.pwhash.Hash()
            try:
                stored_hash.set_hash(self.password)
            except nav.pwhash.InvalidHashStringError:
                # Probably an old style NAV password hash, get out
                # of here and check it the old way
                pass
            else:
                return stored_hash.verify(password)

            # If the stored password looks like an old-style NAV MD5
            # hash we compute the MD5 hash of the supplied password
            # for comparison.
            if self.password[:3] == 'md5':
                hash = md5.md5(password)
                return (hash.hexdigest() == self.password[3:])
            else:
                return (password == self.password)
        else:
            return False

    def setPassword(self, password):
        """Set the password of this account. The password parameter is
        the plaintext password."""
        if len(password.strip()) > 0:
            hash = nav.pwhash.Hash(password=password)
            self.password = str(hash)
        else:
            self.password = ""

class Accountgroup(Accountgroup):
    def getMembers(self):
        """
        Return a list of Account objects that are members of this
        Accountgroup.
        """
        links = self.getChildren(Accountingroup)
        return [Account(link.account) for link in links]

def _customizeTables():
    """
    Customize the output from forgetSQL
    """
    nav.db.forgotten.navprofiles._Wrapper.cursor = nav.db.cursor
    nav.db.forgotten.navprofiles._Wrapper._dbModule = nav.db.driver

    # Fix Privilege
    Privilege._sqlFields['name'] = 'Privilege.privilegename'
    Privilege._sqlFields['id'] = 'Privilege.privilegeid'
    Accountgroupprivilege._sqlPrimary = ('accountgroup', 'privilege', 'target')

    # Fix Accountingroup
    if Accountingroup._sqlFields.has_key('groupid'):
        del Accountingroup._sqlFields['groupid']
    Accountingroup._sqlFields['group'] = 'groupid'
    Accountingroup._userClasses['group'] = Accountgroup
    Accountingroup._sqlPrimary = ('account', 'group')

    # Fix Accountorg
    Accountorg._sqlPrimary = ('account', 'orgid')

    # Fix Accountnavbar
    Accountnavbar._sqlPrimary  =('account', 'navbarlink')

    # Fix Navbarlink
    Navbarlink._sqlPrimary = ('id',)

    # Fix Preference
    Preference._sqlPrimary = ('account',)

    # Fix Accountproperty
    Accountproperty._sqlPrimary = ('account','property','value',)

    # connection with database
    def navprofilesCursor(dummy):
        conn = nav.db.getConnection('default', 'navprofile')
        return conn.cursor()
    setCursorMethod(navprofilesCursor)

def setCursorMethod(cursor):
    import forgotten.navprofiles
    forgotten.navprofiles._Wrapper.cursor = cursor


class NoSuchAccountError(Exception):
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return "No such account %s" % repr(self.login)


##### Initialization #####

_customizeTables()
