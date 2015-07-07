# [START imports]
import os
import urllib
import string
import random
import csv

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras import sessions



import jinja2
import webapp2
from google.storage.speckle.proto.jdbc_type import DISTINCT, NULL
from telnetlib import theNULL
from datetime import date, datetime
from _ast import keyword
from google.appengine.ext.ndb.django_middleware import NdbDjangoMiddleware

# [END imports]

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_CANDIDATE_NAME =''

DEFAULT_SESSION_NUM = 32

DEFAULT_INT = ''

ICS_PASSWORD = "mock1998"

BASE_SESSION_YEAR = 2005

NO_ACCESS_PAGE_HTML = """\
<html>
  <body>
    <form action="/">
      <div>You do not have permission to access this page.</div>
      <div><input type="submit" value="Return"></div>
    </form>
  </body>
</html>
"""

PASS_PAGE_HTML = """\
<html>
  <body>
    <form action="/admin" method="post">
      <div>Please enter the password:</div><br>
      <div><input type="text" name="pwd"></div>
      <div><button type="submit">Submit</button></div>
    </form>
    <a href="/">Return to Main Form</a>
  </body>
</html>
"""
def mapYear(i):
    j = 0
    if (i < 4):
        j = 1
    elif (i < 9):
        j = 2
    else:
        j = 3
    return j


def candidate_key(candidate_id):
    return ndb.Key(Candidate, candidate_id)

def feedback_key(feedback_id):
    return ndb.Key(Feedback, feedback_id)

class Candidate(ndb.Model):
    c_short = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    session_num = ndb.IntegerProperty()

class Interviewer(ndb.Model):
    i_short = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()    
    
class Feedback(ndb.Model):
    """Models feedback from the form"""
    interviewer = ndb.StringProperty()
    company = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    """Ratings"""
    personality_scr = ndb.StringProperty(indexed=False)
    personality_descrip = ndb.StringProperty(indexed=False)
    appearance_scr = ndb.StringProperty(indexed=False)
    appearance_descrip = ndb.StringProperty(indexed=False)
    comm_scr = ndb.StringProperty(indexed=False)
    comm_descrip = ndb.StringProperty(indexed=False)
    tech_scr = ndb.StringProperty(indexed=False)
    tech_descrip = ndb.StringProperty(indexed=False)
    body_scr = ndb.StringProperty(indexed=False)
    body_descrip = ndb.StringProperty(indexed=False)
    """Additional Feedback responses"""
    pres_scr = ndb.StringProperty(indexed=False)
    pres_descrip = ndb.StringProperty(indexed=False)
    exp_scr = ndb.StringProperty(indexed=False)
    rec_descrip = ndb.StringProperty(indexed=False)
    thanks_scr = ndb.StringProperty(indexed=False)
    cycle = ndb.IntegerProperty()
    
# [START main_page]  
class MainPage(webapp2.RequestHandler):
    
    def get(self):
        dNow = datetime.now()
        sNM = dNow.month
        sNY = dNow.year
        sNum = (sNY - BASE_SESSION_YEAR)*3 + mapYear(sNM) + 1
        
        candidate_query = Feedback.query(ndb.GenericProperty('cycle') == int(sNum))
        candidates = candidate_query.fetch(keys_only=True)
        
        cycles = []
        for c in candidates:
                if c.parent() not in cycles:
                    cycles.append(c.parent())
        
        candidates = cycles
        
        interviewer_query = Interviewer.query().order(Interviewer.last_name)
        interviewers = interviewer_query.fetch()

        template_values = {
            'candidates': candidates,
            'interviewers': interviewers,
        }
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

# [END main_page]

class Submission(webapp2.RequestHandler):
    
    def post(self):
        """candidate_name = self.request.get('candidate_name', DEFAULT_CANDIDATE_NAME)
        feedback = Feedback(parent=candidate_key(candidate_name))"""
        
        first_intl = self.request.get("first_name")[:3]
        last_name = self.request.get("last_name")
        
        first_i_intl = self.request.get('int_first_name')[:3]
        last_i_name = self.request.get('int_last_name')
        
        if first_i_intl == "":
            interviewer_id = self.request.get('interviewer')
        else:
            interviewer_id = first_i_intl + last_i_name
            interviewer = Interviewer()
            interviewer.i_short = interviewer_id
            interviewer.first_name = self.request.get('int_first_name')
            interviewer.last_name = self.request.get('int_last_name')
            interviewer.key = ndb.Key(Interviewer, interviewer_id)
            interviewer.put()
        
        
        if first_intl == "":
            candidate_id = self.request.get('candidate')
        else:
            candidate_id = first_intl + last_name
            candidate = Candidate()
            candidate.c_short = candidate_id
            candidate.first_name = self.request.get("first_name")
            candidate.last_name = self.request.get("last_name")
            
            dNow = datetime.now()
            
            sNM = dNow.month
            sNY = dNow.year
            
            sNum = (sNY - BASE_SESSION_YEAR)*3 + mapYear(sNM) + 1
                        
            """candidate.session_num = sNum"""

            candidate.key = ndb.Key(Candidate, candidate_id)
            candidate.put()
        
       
        feedback = Feedback(parent=candidate_key(candidate_id))
        
        feedback.interviewer = interviewer_id
        feedback.company = self.request.get('company')
        """Ratings"""
        feedback.personality_scr = self.request.get('personality_scr')
        feedback.personality_descrip = self.request.get('personality_descrip')
        feedback.appearance_scr = self.request.get('appearance_scr')
        feedback.appearance_descrip = self.request.get('appearance_descrip')
        feedback.comm_scr = self.request.get('comm_scr')
        feedback.comm_descrip = self.request.get('comm_descrip')
        feedback.tech_scr = self.request.get('tech_scr')
        feedback.tech_descrip = self.request.get('tech_descrip')
        feedback.body_scr = self.request.get('body_scr')
        feedback.body_descrip = self.request.get('body_descrip')
        """Additional Feedback responses"""
        feedback.pres_scr = self.request.get('pres_scr')
        feedback.pres_descrip = self.request.get('pres_descrip')
        feedback.exp_scr = self.request.get('exp_scr')
        feedback.rec_descrip = self.request.get('rec_descrip')
        feedback.thanks_scr = self.request.get('thanks_scr')
        
        dNow = datetime.now()  
        sNM = dNow.month
        sNY = dNow.year
        sNum = (sNY - BASE_SESSION_YEAR)*3 + mapYear(sNM) + 1
        feedback.cycle = sNum
        
        feedback.put()
        
        self.redirect('/thanks')

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class Administrate(BaseHandler):
           
    def get(self):
        cSess = self.session.get('currSess')
        
        if cSess == None:
            template = JINJA_ENVIRONMENT.get_template('return.html')
            self.response.write(template.render())
        else:
            curI = self.request.get('interviewer', DEFAULT_INT)
            curS = self.request.get("session", DEFAULT_SESSION_NUM)
            if curS != '':
                curS = curS
            else:
                curS = DEFAULT_SESSION_NUM        
            candidate_query_s = Feedback.query(ndb.GenericProperty('cycle') == int(curS))
            candidates_s = candidate_query_s.fetch(keys_only=True) 
            candidate_query_i = Feedback.query(ndb.GenericProperty('interviewer') == curI)
            candidates_i = candidate_query_i.fetch(keys_only=True)
            
            if candidate_query_i.count() == 0:
                sel_mes_i = "There are no candidates for this interviewer..."
            else:
                sel_mes_i = "Please select a candidate..."
            
            inters = []
            for inter in candidates_i:
                if inter.parent() not in inters:
                    inters.append(inter.parent())
            
            candidates_i = inters
            
                
            if candidate_query_s.count() == 0:
                sel_mes = "There are no candidates for this cycle..."
            else:   
                sel_mes = "Please select a candidate..."
            
            cycles = []
            for c in candidates_s:
                if c.parent() not in cycles:
                    cycles.append(c.parent())
            
            candidates_s = cycles
            
            candidate = self.request.get('candidate', DEFAULT_CANDIDATE_NAME)
            if candidate != "":
                report_query = Feedback.query(ancestor=candidate_key(candidate)).order(-Feedback.date)
                reports = report_query.fetch()
            else:
                reports = ""
                curCand = "" 
            
            if candidate == 'all':
                report_query = Feedback.query().order(-Feedback.date)
                reports = report_query.fetch()
                curCand = candidate_key(candidate).get()
            
            inter_query = Interviewer.query().order(-Interviewer.last_name)
            interviewers = inter_query.fetch()
            
            dNow = datetime.now()
            sNM = dNow.month
            sNY = dNow.year
            sNum = (sNY - BASE_SESSION_YEAR)*3 + mapYear(sNM)
               
            
            template_values = {
                'bYr': BASE_SESSION_YEAR,
                'curS': curS,
                'sel_mes': sel_mes,
                'sel_mes_i':sel_mes_i,
                'sessions': sNum,
                'curCand': curCand,
                'candidates_s': candidates_s,
                'candidates_i': candidates_i,
                'interviewers': interviewers,
                'reports': reports,
                'curI': curI,
            }
            
            template = JINJA_ENVIRONMENT.get_template('admin.html')
            self.response.write(template.render(template_values))
        
class Report (BaseHandler):
    
    def post(self):
        candidate = self.request.get('candidate')
        self.response.write(candidate)
        interviewer = self.request.get('interviewer')
        self.response.write(interviewer)
        session = self.request.get('session')
        self.response.write(session)
        query_params = {'candidate' : candidate,
                        'interviewer':interviewer,
                        'session':session}
        self.redirect('admin?' + urllib.urlencode(query_params))

class Writer (webapp2.RequestHandler):
    
    def get(self):
        
        reps = self.request.get_all('repID')
        
        self.response.headers['Content-Type'] = 'application/csv'
        self.response.headers['Content-Disposition'] = 'attachment; filename=Extract_'+ datetime.ctime(datetime.now())+'.csv'
        writer = csv.writer(self.response.out)

        writer.writerow(["candidate", "date", "interviewer", "company", "personality_scr",
                         "personality_descrip", "appearance_scr", "appearance_descrip",
                         "comm_scr", "comm_descrip","tech_scr","tech_descrip","body_scr",
                         "body_descrip","pres_scr","pres_descrip","exp_scr","rec_descrip"])
        
        for rep in reps:
            rep_name = rep[:rep.find("|")]
            rep_num = rep[rep.find("|")+1:]
            rep_key = ndb.Key('Candidate', rep_name, 'Feedback', int(rep_num))
            r = rep_key.get()
            r_name = r.key.parent().get().last_name +", "+ r.key.parent().get().first_name
            writer.writerow([r_name, r.date, r.interviewer, r.company, r.personality_scr,
                             r.personality_descrip, r.appearance_scr, r.appearance_descrip,
                             r.comm_scr, r.comm_descrip, r.tech_scr, r.tech_descrip, r.body_scr,
                             r.body_descrip, r.pres_scr, r.pres_descrip, r.exp_scr, r.rec_descrip])          

class PassPage (BaseHandler):
    
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render())
    
    def post(self):
        pwd = self.request.get('pwd')
        if pwd != ICS_PASSWORD:
            log_fail = "Sorry, that password was incorrect. Please try again:"
            template_values = {
                 'log_fail': log_fail,              
                               }
            template = JINJA_ENVIRONMENT.get_template('login.html')
            self.response.write(template.render(template_values))
        else:
            self.session['currSess'] = "".join(random.choice(string.ascii_uppercase) for i in range(12))
            self.redirect('/admin')      

class Thanks (BaseHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('thanks.html')
        self.response.write(template.render())

class Logoff (BaseHandler):
    def get(self):
        self.session.clear()
        self.redirect("/")


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'QPBZOSYOKHHA',
    'session_max_age': 3600,
}
        
application = webapp2.WSGIApplication([
        ('/', MainPage),
        ('/sign', Submission),
        ('/admin', Administrate),
        ('/pass', PassPage),
        ('/report', Report),
        ('/logoff', Logoff),
        ('/writer', Writer),
        ('/thanks', Thanks),
], debug=True, config=config)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

