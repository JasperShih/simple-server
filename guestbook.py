import cgi
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Sign Guestbook"></div>
      <input type="text" name="userNick" placeholder="Input your nickname" />
    </form>
    <hr>
    <form>Guestbook name:
      <input value="%s" name="guestbook_name">
      <input type="submit" value="switch">
    </form>
    <a href="%s">%s</a>
  </body>
</html>
"""

modifyH="""\
<a href="/blank?%s">Modify</a>
"""

blankHTML="""\
<html>
    <body>
        <form action="/modify?%s" method="post">
        <div><textarea name="content" rows="3" cols="60"></textarea></div>
        <div><input type="submit" value="Submit" /></div>
        </form>
    </body>
</html>
"""

deleteH="""\
<a href="/delete?%s">Delete</a><br>
"""

alert="""\
<script type="text/javascript">
alert('You can not submit empty content!')
window.location.href = "/"
</script>

"""

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        #Account.query(Account.userid == 42)
        #greetings_query = Greeting.query(Greeting.content == "hi")
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        #greetings[0].key.delete()
        #greetings[0].content="hhh"

        count=0
        for greeting in greetings:
            if greeting.author:
                self.response.write('<b>%s</b> wrote:' % greeting.author.nickname())
            else:
                self.response.write('An anonymous person wrote:')
            self.response.write('<blockquote>%s</blockquote>' % greeting.content)
            #self.response.write('<blockquote>%s</blockquote>' % cgi.escape(greeting.content))

            if users.get_current_user()!=None and users.get_current_user()==greeting.author:
                #self.response.write(greeting.author)
                countBookH = {'count': str(count),'guestbook_name':guestbook_name}
                #countH = {'count': str(count)}
                self.response.write(modifyH % (urllib.urlencode(countBookH)))
                self.response.write(deleteH % (urllib.urlencode(countBookH)))

            count+=1


        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %
                            (sign_query_params, cgi.escape(guestbook_name),
                             url, url_linktext))

class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))
        #Creat Greeting obj and set Greeting obj parent
        if users.get_current_user():
            greeting.author = users.get_current_user()
        elif self.request.get('userNick')!="":
            user = users.User(self.request.get('userNick'))
            greeting.author=user

        content=self.request.get('content')

        if content==" " or content=="\t" or content=="":
            self.response.write(alert)
        else:
            greeting.content = content.replace("\n","<br>")
            greeting.put()
            query_params = {'guestbook_name': guestbook_name}
            self.redirect('/?' + urllib.urlencode(query_params))##########################################

class DeleteF(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        count = self.request.get('count')
        greetings[int(count)].key.delete()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))



class BlankF(webapp2.RequestHandler):
    def get(self):
        count = self.request.get('count')
        guestbook_name = self.request.get('guestbook_name')

        countBookH = {'count': str(count),'guestbook_name':guestbook_name}

        self.response.write(blankHTML % (urllib.urlencode(countBookH)))

        #self.response.write(blankHTML)




class ModifyF(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name',DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        count = self.request.get('count')

        #self.response.write(self.request.get('content'))
        greetings[int(count)].content=self.request.get('content')
        greetings[int(count)].put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/delete',DeleteF),
    ('/blank',BlankF),
    ('/modify',ModifyF),

], debug=True)

