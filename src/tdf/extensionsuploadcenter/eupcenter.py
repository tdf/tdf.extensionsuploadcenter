from five import grok
from zope import schema

from zope.component import createObject
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.filerepresentation.interfaces import IFileFactory

from plone.indexer import indexer

from plone.directives import form, dexterity
from plone.app.textfield import RichText

from plone.formwidget.autocomplete import AutocompleteFieldWidget
from z3c.form.browser.textlines import TextLinesFieldWidget

from tdf.extensionsuploadcenter import _

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from Acquisition import aq_inner
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent
from tdf.extensionsuploadcenter.eupproject import IEUpProject

from plone.app.layout.viewlets.interfaces import IAboveContentTitle
from plone import api



class IEUpCenter(form.Schema):

    """ An Extensions Upload Center for LibreOffice extensions.
    """



    title= schema.TextLine(
        title=_(u"Name of the Extensions Center"),
    )

    description=schema.Text(
        description=_(u"Description of the Extensions Center"),
    )

    product_description=schema.Text(
        description=_(u"Description of the features of extensions")
    )


    product_title = schema.TextLine(
        title=_(u"Extension Product Name"),
        description=_(u"Name of the Extension product, e.g. only Extensions or LibreOffice Extensions"),
    )

    development_status = schema.List(title=_(u"Development Status"),
        default=['Planing',
                 'Pre-Alpha',
                 'Alpha',
                 'Beta',
                 'Production/Stable',
                 'Mature',
                 'Inactive'],
        value_type=schema.TextLine()
    )

    available_category = schema.List(title=_(u"Available Categories"),
        default=['Gallery Contents',
                 'Language Tools',
                 'Dictionary',
                 'Writer_Extension',
                 'Calc_Extension',
                 'Impress_Extension',
                 'Draw_Extension',
                 'Base_Extension',
                 'Math_Extension',
                 'Extension_Building',
                 'All modules'],

        value_type=schema.TextLine())


    available_licenses =schema.List(title=_(u"Available Licenses"),
        default=['GNU-GPL-v2 (GNU General Public License Version 2)',
                 'GNU-GPL-v3 (General Public License Version 3)',
                 'LGPL-v2.1 (GNU Lesser General Public License Version 2.1)',
                 'LGPL-v3+ (GNU Lesser General Public License Version 3 and later)',
                 'BSD (BSD License (revised))',
                 'MPL-v1.1 (Mozilla Public License Version 1.1',
                 'MPL-v2.0 (Mozilla Public License Version 2.0',
                 'CC-by-sa-v3 (Creative Commons Attribution-ShareAlike 3.0)',
                 'OSI (Other OSI Approved)'],
        value_type=schema.TextLine())

    available_versions = schema.List(title=_(u"Available Versions"),
        default=['LibreOffice 3.3',
                 'LibreOffice 3.4',
                 'LibreOffice 3.5',
                 'LibreOffice 3.6',
                 'LibreOffice 4.0',
                 'LibreOffice 4.1',
                 'LibreOffice 4.2',
                 'LibreOffice 4.3',
                 'LibreOffice 4.4',
                 'LibreOffice 5.0'],
        value_type=schema.TextLine())

    available_platforms = schema.List(title=_(u"Available Platforms"),
        default=['All platforms',
                 'Linux',
                 'Linux-x64',
                 'Mac OS X',
                 'Windows',
                 'BSD',
                 'UNIX (other)'],
         value_type=schema.TextLine())

    form.primary('install_instructions')
    install_instructions = RichText(
        title=_(u"Extension Installation Instructions"),
        default=_(u"Fill in the install instructions"),
        required=False
    )

    form.primary('reporting_bugs')
    reporting_bugs = RichText(
        title=_(u"Instruction how to report Bugs"),
        required=False
    )

    title_legaldisclaimer = schema.TextLine(
        title=_(u"Title for Legal Disclaimer and Limitations"),
        default=_(u"Legal Disclaimer and Limitations"),
        required=False
    )


    form.primary('legal_disclaimer')
    legal_disclaimer = RichText(
        title=_(u"Text of the Legal Disclaimer and Limitations"),
        description=_(u"Enter the text of the legal disclaimer and limitations that should be displayed to the project creator and should be accepted by the owner of the project."),
        default=_(u"Fill in the legal disclaimer, that had to be accepted by the project owner"),
        required=False
    )

    title_legaldownloaddisclaimer = schema.TextLine(
        title=_(u"Title of the Legal Disclaimer and Limitations for Downloads"),
        default=_(u"Legal Disclaimer and Limitations for Downloads"),
        required=False
    )

    form.primary('legal_downloaddisclaimer')
    legal_downloaddisclaimer = RichText(
        title=_(u"Text of the Legal Disclaimer and Limitations for Downlaods"),
        description=_(u"Enter any legal disclaimer and limitations for downloads that should appear on each page for dowloadable files."),
        default=_(u"Fill in the text for the legal download disclaimer"),
        required=False
    )

@grok.subscribe(IEUpProject,IObjectAddedEvent)
def notifyAboutNewProject(eupproject, event):
    mailhost = getToolByName(eupproject, 'MailHost')
    urltool = getToolByName(eupproject, 'portal_url')
    portal = urltool.getPortalObject()
    toAddress = portal.getProperty('email_from_address')
    message = "A member added a new project"
    subject = "A Project with the title %s was added" % (eupproject.title)
    source = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org')
    return mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject, charset='utf8')


@grok.subscribe(IEUpCenter, IObjectModifiedEvent)
def notifiyAboutNewVersion(eupproject, event):
    if hasattr(event, 'descriptions') and event.descriptions:
        for d in event.descriptions:
            if d.interface is IEUpCenter and 'available_versions' in d.attributes:
                users=api.user.get_users()
                message='We added a new version of LibreOffice to the list.\n' \
                        'Please add this version to your LibreOffice extension release(s), ' \
                        'if it is (they are) compatible with this version.\n\n' \
                        'Kind regards,\n\n' \
                        'The LibreOffice Extension and Template Site Administration Team'
                for f in users:
                    mailaddress = f.getProperty('email')
                    api.portal.send_email(
                        recipient=mailaddress,
                        sender="noreply@libreoffice.org",
                        subject="New Version of LibreOffice Added",
                        body=message,
                    )



# Views

class View(dexterity.DisplayForm):
    grok.context(IEUpCenter)
    grok.require('zope2.View')



    def eupprojects(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return catalog(object_provides=IEUpProject.__identifier__,
             path='/'.join(context.getPhysicalPath()),
             sort_order='sortable_title')


    def eupproject_count(self):
        """Return number of projects
        """
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return len(catalog(portal_type='tdf.extensionsuploadcenter.eupproject'))


    def euprelease_count(self):
        """Return number of downloadable files
        """
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')

        return len(catalog(portal_type='tdf.extensionsuploadcenter.euprelease'))


    def get_latest_program_release(self):
        """Get the latest version from the vocabulary. This only
        goes by string sorting so would need to be reworked if the
        LibreOffice versions dramatically changed"""
        
        versions = list(self.context.available_versions)
        versions.sort(reverse=True)
        return versions[0]


    def get_products(self, category, version, sort_on, SearchableText=None):
        self.catalog = getToolByName(self.context, 'portal_catalog')

        sort_on = 'positive_ratings'

        contentFilter = {
	                     'sort_on' : sort_on,
                         
                         'SearchableText': SearchableText,
	                     'sort_order': 'reverse',
                         'portal_type': 'tdf.extensionsuploadcenter.eupproject'}

        if version != 'any':
            contentFilter['getCompatibility'] = version

        if category:
            contentFilter['getCategories'] = category

        return self.catalog(**contentFilter)




    def get_most_popular_products(self):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        sort_on = 'positive_ratings'
        contentFilter = {
                         'sort_on' : sort_on,
                         'sort_order': 'reverse',
                         'review_state': 'published',
                         'portal_type' : 'tdf.extensionsuploadcenter.eupproject'}
        return self.catalog(**contentFilter)


    def get_newest_products(self):
        self.catalog = getToolByName(self.context, 'portal_catalog')
        sort_on = 'created'
        contentFilter = {
                          'sort_on' : sort_on,
                          'sort_order' : 'reverse',
                          'review_state': 'published',
                          'portal_type':'tdf.extensionsuploadcenter.eupproject'}

        results = self.catalog(**contentFilter)

        return results


    def category_name(self):
        category = list(self.context.available_category)
        return category



class eupownprojects(grok.Viewlet):
    grok.context(IEUpCenter)
    grok.viewletmanager(IAboveContentTitle)
    grok.template('own_project')
    grok.order(1)
    grok.require('zope2.View')



