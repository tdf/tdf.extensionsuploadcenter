from five import grok
from zope.interface import implements
from tdf.extensionsuploadcenter.interfaces import INameForRelease


class NameForRelease(object):
    """ Adapter to INameFromTitle
    """

    implements(INameForRelease)

    def __init__(self, context):
        self.context = context

    def __new__(cls, context):
        title = context.title
        releasenumber = context.releasenumber
        title = u'%s %s' % (title,releasenumber)
        releasename = super(NameForRelease, cls).__new__(cls)
        releasename.title = title
        return releasename
