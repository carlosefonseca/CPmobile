from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication

from myTrain.handlers import TestThing
from CP import CP
from Refer import Refer

auth = HttpBasicAuthentication(realm="My Realm")
ad = {  }

# blogpost_resource = Resource(handler=BlogPostHandler, **ad)
# arbitrary_resource = Resource(handler=ArbitraryDataHandler, **ad)
test_thing = Resource(handler=TestThing, **ad)
cp_resource = Resource(handler=CP, **ad)
refer_resource = Resource(handler=Refer, **ad)

# url(r'^posts/(?P<post_slug>[^/]+)/$', blogpost_resource), 
# url(r'^other/(?P<username>[^/]+)/(?P<data>.+)/$', arbitrary_resource), 
 
urlpatterns = patterns('',
	(r'^test/(?P<var1>[^/]+)$', test_thing),
	(r'^cp/(?P<action>[^/?]+)/?$', cp_resource),
	(r'^refer/(?P<action>[^/?]+)/?$', refer_resource)
)

