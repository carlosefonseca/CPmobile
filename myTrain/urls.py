from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from Handler import Handler

auth = HttpBasicAuthentication(realm="My Realm")
ad = {  }

# blogpost_resource = Resource(handler=BlogPostHandler, **ad)
# arbitrary_resource = Resource(handler=ArbitraryDataHandler, **ad)
handler_resource = Resource(handler=Handler, **ad)

# url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource), 
# url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource), 
 
urlpatterns = patterns('',
	(r'^(?P<action>[^/?]*)/?$', handler_resource)
)

