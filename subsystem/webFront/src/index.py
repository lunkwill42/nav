"""
$Id$

This file is part of the NAV project.

This module represents the page index of the NAV web interface.  It
follows the mod_python.publisher paradigm.

Copyright (c) 2003 by NTNU, ITEA nettgruppen
Authors: Morten Vold <morten.vold@itea.ntnu.no>

"""
from mod_python import apache
import os
import nav
from nav import web

welcomeFileAnonymous = "/usr/local/nav/navme/apache/webroot/frontpage/welcome-anonymous.txt"
welcomeFileRegistered = "/usr/local/nav/navme/apache/webroot/frontpage/welcome-registered.txt"
contactInformationFile = "/usr/local/nav/navme/apache/webroot/frontpage/contact-information.txt"
externalLinksFile = "/usr/local/nav/navme/apache/webroot/frontpage/external-links.txt"
navLinksFile = "/usr/local/nav/navme/apache/webroot/frontpage/nav-links.conf"

TIMES = [' seconds', ' minutes', ' hours', ' days', ' years']

def index(req):
    if req.session.has_key('user'):
        name = req.session['user'].name
    else:
        name = req.session.id

    from nav.web.templates.FrontpageTemplate import FrontpageTemplate

    page = FrontpageTemplate()
    page.path = [("Frontpage", False)]

    if req.session['user'].id == 0:
        welcomeFile = welcomeFileAnonymous
    else:
        welcomeFile = welcomeFileRegistered
    page.welcome = lambda:file(welcomeFile).read()
    page.externallinks = lambda:file(externalLinksFile).read()
    page.contactinformation = lambda:file(contactInformationFile).read()

    navlinks = nav.config.readConfig(navLinksFile)
    navlinkshtml = ""
    for name, url in navlinks.items():
        if (nav.web.linkchecker.shouldShow(url, req.session['user'])):
            navlinkshtml = navlinkshtml + "<a href=\"%s\">%s</a><br>" % (url, name)
    page.navlinks = lambda:navlinkshtml

    from nav import getstatus
    liste = nav.getstatus.boxesDownSortByNewest()
    numboxesdown = 0
    numboxesshadow = 0
    for box in liste:
        timeparts = str(box[0]).split(':')
        time = timeparts[0] + TIMES[len(timeparts)-1]
        box.append(time)
        if box[4]:
            numboxesshadow = numboxesshadow + 1
        else:
            numboxesdown = numboxesdown + 1
    page.boxesdown = liste
    page.numboxesdown = numboxesdown
    page.numboxesshadow = numboxesshadow

    return page

def login(req, login='', password='', origin=''):
    """
    Handles the login page
    """
    if login:
        # The user is attempting to log in, and we want to be sure
        # that any existing Account objects in this session are
        # deleted:
        if req.session.has_key('user'):
            del req.session['user']
            req.session.save()
        
        from nav import db
        conn = db.getConnection('navprofile', 'navprofile')
        from nav.db import navprofiles
        navprofiles.setCursorMethod(conn.cursor)
        from nav.db.navprofiles import Account

        try:
            account = Account.loadByLogin(login)
        except nav.db.navprofiles.NoSuchAccountError:
            return _getLoginPage(origin, "Login failed")

        if (account.authenticate(password)):
            # Place the Account object in the session dictionary
            req.session['user'] = account
            req.session.save()

            # Redirect to the origin page, or to the root if one was
            # not given (using the refresh header, so as not to screw
            # up the client's POST operation)
            if not origin.strip():
                origin = '/'
            web.redirect(req, origin, seeOther=True)
        else:
            return _getLoginPage(origin, "Login failed")
    else:
        # The user requested only the login page
        if origin:
            return _getLoginPage(origin, "Not authorized")
        else:
            return _getLoginPage('')

def _getLoginPage(origin, message=''):
    from nav.web.templates.LoginTemplate import LoginTemplate
    page = LoginTemplate()

    page.origin = origin
    page.message = message
    
    return page

def logout(req):
    """
    Expires the current session, removes the session cookie and redirects to the index page.
    """
    # Expire and remove session
    req.session.expire()
    del req.session
    from nav.web import state
    state.deleteSessionCookie(req)

    # Redirect user to root page
    req.headers_out['Location'] = '/'
    req.status = apache.HTTP_TEMPORARY_REDIRECT
    req.send_http_header()
    raise apache.SERVER_RETURN, apache.HTTP_TEMPORARY_REDIRECT
