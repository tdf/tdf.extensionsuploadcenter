from zope.interface import Invalid, invariant

from five import grok
from zope import schema
from tdf.extensionsuploadcenter import _
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from collective import dexteritytextindexer
from zope.schema.interfaces import IContextSourceBinder
import re
from plone.namedfile.field import NamedBlobImage
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import validator
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.validation import V_REQUIRED
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from tdf.extensionsuploadcenter.euprelease import IEUpRelease
from plone.indexer import indexer



checkEmail = re.compile(
    r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}").match

def validateEmail(value):
    if not checkEmail(value):
        raise Invalid(_(u"Invalid email address"))
    return True


@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabCategories(context):
    # For add forms

    # For other forms edited or displayed
    from tdf.extensionsuploadcenter.eupcenter import IEUpCenter
    while context is not None and not IEUpCenter.providedBy(context):
        #context = aq_parent(aq_inner(context))
        context = context.__parent__

    category_list = []
    if context is not None and context.available_category:
        category_list = context.available_category

    terms = []
    for value in category_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))

    return SimpleVocabulary(terms)


def isNotEmptyCategory(value):
    if not value:
        raise Invalid(u'You must choose at least one category for your project.')
    return True




class MissingCategory(Invalid):
    __doc__ = _(u"You have not chosen a category for the project")

class IEUpProject(form.Schema):


    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Project Title - minimum 5 and maximum 40 characters"),
        min_length=5,
        max_length=40
    )

    description = schema.Text(
        title=_(u"Project Summary"),
    )


    form.primary('details')
    details = RichText(
        title=_(u"Full Project Description"),
        required=False
    )

    dexteritytextindexer.searchable('category_choice')
    category_choice = schema.List(
        title=_(u"Choose your categories"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabCategories),
        constraint = isNotEmptyCategory,
        required=True
    )


    contactAddress=schema.ASCIILine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        constraint=validateEmail
    )

    homepage=schema.URI(
        title=_(u"Homepage"),
        description=_(u"If the project has an external home page, enter its URL (example: 'http://www.mysite.org')."),
        required=False
    )

    documentation_link=schema.URI(
        title=_(u"URL of documentation repository "),
        description=_(u"If the project has externally hosted documentation, enter its URL (example: 'http://www.mysite.org')."),
        required=False
    )

    project_logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(u"Add a logo for the project (or organization/company) by clicking the 'Browse' button."),
        required=False,
    )

    screenshot = NamedBlobImage(
        title=_(u"Screemshot of the Extension"),
        description=_(u"Add a screenshot by clicking the 'Browse' button."),
        required=False,
    )


@grok.subscribe(IEUpProject, IActionSucceededEvent)
def notifyProjectManager (eupproject, event):
    mailhost = getToolByName(eupproject, 'MailHost')
    toAddress = "%s" % (eupproject.contactAddress)
    message= "The status of your LibreOffice extension project changed"
    subject = "Your Project %s" % (eupproject.title)
    source = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org')
    return mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject, charset='utf8')

@grok.subscribe(IEUpRelease,IObjectAddedEvent)
def notifyProjectManagerReleaseAdd (eupproject, event):
    mailhost = getToolByName(eupproject, 'MailHost')
    toAddress = "%s" % (eupproject.contactAddress)
    message = "The new release %s was added to your LibreOffice extension project" % (eupproject.title)
    subject = "A new release was added to your LibreOffice extension project"
    source = "%s <%s>" % ('Admin of the LibreOffice Extensions site', 'extensions@libreoffice.org')
    return mailhost.send(message, mto=toAddress, mfrom=str(source), subject=subject, charset='utf8')


def getLatestRelease(self):

    res = None
    catalog = getToolByName(self, 'portal_catalog')
    res = catalog.searchResults(
        folderpath = '/'.join(context.getPhysicalPath()),
        review_state = 'published',
        sort_on = 'Date',
        sort_order = 'reverse',
        portal_type = 'tdf.extensionsuploadcenter.euprelease')

    if not res:
        return None
    else:
        return res[0]

@grok.adapter(IEUpProject, name='getCompatibility')
@indexer(IEUpProject)
def getCompatibilityIndexer(obj):
    """Get the compatibility of the product by getting the compatibilities of the latest published release.
    This is been used for the index"""

    compatabilities = []
    release = obj.getLatestRelease()
    if release:
        for release_compatability in release.getCompatibility:
            compatabilities.append(release_compatability)
    compatabilities.sort(reverse=True)
    return set(compatabilities)


class ValidateEUpProjectUniqueness(validator.SimpleFieldValidator):
    #Validate site-wide uniqueness of project titles.


    def validate(self, value):
        # Perform the standard validation first
        super(ValidateEUpProjectUniqueness, self).validate(value)

        if value is not None:
            catalog = getToolByName(self.context, 'portal_catalog')
            results = catalog({'Title': value,
                               'object_provides': IEUpProject.__identifier__})

            contextUUID = IUUID(self.context, None)
            for result in results:
                if result.UID != contextUUID:
                    raise Invalid(_(u"The project title is already in use"))

validator.WidgetValidatorDiscriminators(
    ValidateEUpProjectUniqueness,
    field=IEUpProject['title'],
)
grok.global_adapter(ValidateEUpProjectUniqueness)

# View

class View(dexterity.DisplayForm):
    grok.context(IEUpProject)
    grok.require('zope2.View')
