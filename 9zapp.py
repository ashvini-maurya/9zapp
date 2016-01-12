import cgi
import urllib
import webapp2

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers



class Greeting(ndb.Model):
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(cls.date)




class UserPhoto(ndb.Model):
    blob_key = ndb.BlobKeyProperty()
    like=ndb.IntegerProperty(default=0)
    unlike=ndb.IntegerProperty(default=0)
    extension=ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def query_book(cls, ancestor_key):
        return cls.query(ancestor=ancestor_key).order(-cls.date)





class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')

        photos=UserPhoto.query_book(ndb.Key("Photo","*notitle*")).fetch(20)
        for photo in photos:
                    likeValue=photo.like
                    unlikeValue=photo.unlike
                    if photo.extension in ['.gif', '.jpe', '.jpeg', '.jpg','.png','.img']:
                            self.response.out.write('<html><body><img style="width:300px;height=250px "  src="/serve/%s"></body></html>'% photo.blob_key)
                    elif photo.extension in ['.mkv','.flv','.avi','.mov','.wmv','.mp4','.3gp']:
                            self.response.out.write('<html><body><video width="320" height="240" controls><source src="/serve/%s" type="video/mp4">Your browser does not support the video tag.</video></body></html>'% photo.blob_key)

                    if(self.request.get('likekey') == '1' and self.request.get('picUrl') == photo.blob_key):
                        likeValue=photo.like+1
                        photo.like=likeValue
                        photo.put()
                        self.redirect('/')

                    elif(self.request.get('unlikekey') == '1' and self.request.get('picUrl') == photo.blob_key):
                        unlikeValue=photo.unlike+1
                        photo.unlike=unlikeValue
                        photo.put()
                        self.redirect('/')

                    #self.response.out.write('%s<br>' % photo.date)
                    self.response.out.write('<a href="/?likekey=1&&picUrl=%s">likes   </a>%d' % (photo.blob_key,likeValue))
                    self.response.out.write('&nbsp;&nbsp;&nbsp;&nbsp;<a href="/?unlikekey=1&&picUrl=%s">unlikes   </a>%d'% (photo.blob_key,unlikeValue))
                    greetings=Greeting.query_book(ndb.Key("book",str(photo.blob_key) or "*notitle*")).fetch(20)
                    self.response.out.write('<br>Comments : %d'% len(greetings))



                    for greeting in greetings:
                            self.response.out.write('<blockquote>%s</blockquote>' %
                                    cgi.escape(greeting.content))
                    self.response.out.write("""
          <form action="/sign?guest_id=%s" method="post">
            <div><textarea name="content" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="comment"></div>
          </form>
          <hr>
          """% str(photo.blob_key))


        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)

        self.response.out.write("""Upload File:
                <input type="file" name="file"><br> <input type="submit"
                name="submit" value="Submit"> </form></body></html>""")



import os
import imghdr
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        # 'file' is file upload field in the form

      try:
        upload_files = self.get_uploads('file')
        # self.request.POST.multi['file'].file.read()
        format_extension=os.path.splitext(self.request.POST.getall('file')[0].filename)[1]
        for_ext=format_extension.lower()
        mylist=['.gif', '.jpe', '.jpeg', '.jpg','.png','.img' ,'.mkv','.flv','.avi','.mov','.wmv','.mp4','.3gp']
        if for_ext in mylist:
            blob_info = upload_files[0]
            photo=UserPhoto(parent=ndb.Key("Photo" ,"*notitle*"),blob_key=blob_info.key(),extension=for_ext)
            photo.put()

            self.response.out.write('<html><body><img style="width:200px; "  src="/serve/%s"></body></html>'% blob_info.key())
            self.redirect('/')
        else:
            self.response.out.write('You are allowed to upload only images and videos.')
            self.response.out.write('&nbsp;&nbsp;&nbsp;&nbsp;<a href="/">Back</a>')


      except:
          self.response.out.write('Please select a file: &nbsp;&nbsp;&nbsp;&nbsp;<a href="/">Back</a>')




class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)



        self.send_blob(blob_info)

class SubmitForm(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guest_id')
        greeting = Greeting(parent=ndb.Key("book" ,guestbook_name or "*notitle*"),content=self.request.get('content'))
        greeting.put()
        self.redirect('/')


















# #
# #
# #
# import base64
# import datetime
# import logging
# import time
# import urllib
# import webapp2
# from google.appengine.api.logservice import logservice
# from google.appengine.api import mail
#
# class MainHandler(webapp2.RequestHandler):
#     def get(self):
#       # Set up end time for our query.
#       end_time = time.time()
#       start_time = end_time  - 120    # 3 hours before now . same as cronjob interval
#       html = ''
#       report_needed = False
#
#       for req_log in logservice.fetch(start_time=start_time, end_time=end_time, minimum_log_level=logservice.LOG_LEVEL_WARNING, include_app_logs=True):
#             report_needed = True
#             html = html + '<br /> REQUEST LOG <br />'
#             html = html + 'IP: %s <br /> Method: %s <br /> Resource: %s <br />' % (req_log.ip, req_log.method, req_log.resource)
#             html = html + 'Date: %s<br />' % datetime.datetime.fromtimestamp(req_log.end_time).strftime('%D %T UTC')
#
#             for app_log in req_log.app_logs:
#                 html = html + '<br />&emsp; APP LOG<br />'
#                 html = html + '&emsp; Date: %s<br />' % datetime.datetime.fromtimestamp(app_log.time).strftime('%D %T UTC')
#                 html = html + '&emsp; Message: <b>%s</b><br />' % app_log.message
#                 html = html + '<br /><br /><br /><br />'
#       if(report_needed):
#            mail.send_mail(sender="Beagle Bot <bot@urdomain.com>",
#                 to='ashvinikumar45@gmail.com',
#                 subject='every hour summary job from 9zapp',
#                 body=html,
#                 html=html,
#                 reply_to='support@urdomain.com')
#       self.response.out.write(html)
#
# # app = webapp2.WSGIApplication([('/errorfinder/', MainHandler)], debug=True)
# #
#
#
#















app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', SubmitForm),
    ('/upload', UploadHandler),
     ('/serve/([^/]+)?', ServeHandler),
    #('/errorfinder/', MainHandler),
], debug=True)