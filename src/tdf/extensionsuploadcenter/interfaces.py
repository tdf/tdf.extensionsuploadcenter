from plone.app.content.interfaces import INameFromTitle

class INameForRelease(INameFromTitle):

    def title():
        """Return a custom title for release"""
