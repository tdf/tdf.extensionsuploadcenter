from five import grok
from zope import schema
from tdf.extensionsuploadcenter import _
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.security import checkPermission
from zope.interface import invariant, Invalid
from Acquisition import aq_inner, aq_parent, aq_get, aq_chain
from plone.namedfile.field import NamedBlobFile




@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabDevelopmentStatus(context):
    """pick up developmnet status from parent"""
    developmentstatus_list = getattr(context.__parent__, 'development_status', [])
    terms = []
    for value in developmentstatus_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)



@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabAvailLicenses(context):
    """ pick up licenses list from parent """

    license_list = getattr(context.__parent__, 'available_licenses', [])
    terms = []
    for value in license_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)

@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabAvailVersions(context):
    """ pick up the program versions list from parent """

    versions_list = getattr(context.__parent__, 'available_versions', [])
    terms = []
    for value in versions_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)

@grok.provider(schema.interfaces.IContextSourceBinder)
def vocabAvailPlatforms(context):
    """ pick up the list of platforms from parent """

    platforms_list = getattr(context.__parent__, 'available_platforms', [])
    terms = []
    for value in platforms_list:
        terms.append(SimpleTerm(value, token=value.encode('unicode_escape'), title=value))
    return SimpleVocabulary(terms)




yesnochoice = SimpleVocabulary(
    [SimpleTerm(value=0, title=_(u'No')),
     SimpleTerm(value=1, title=_(u'Yes')),]
    )

def isNotEmptyLicenseChoice(value):
     if not value:
         raise Invalid(u"You had to choose at least one license for your release.")
     return True


def isNotEmptyCompatibilityChoice(value):
    if not value:
        raise Invalid(u"You had to choose at least one product version for your release.")
    return True


class AcceptLegalDeclaration(Invalid):
    __doc__ = _(u"It is necessary that you accept the Legal Declaration")



class IEUpRelease(form.Schema):



    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Release Title"),
        min_length=5
    )

    releasenumber=schema.Int(
        title=_(u"Release Number"),
        description=_(u"Release Number"),
        default=1,
    )


    description = schema.Text(
        title=_(u"Release Summary"),
    )



    form.primary('details')
    details = RichText(
        title=_(u"Full Release Description"),
        required=False
    )



    form.primary('changelog')
    changelog = RichText(
        title=_(u"Changelog"),
        description=_(u"A detailed log of what has changed since the previous release."),
        required=False,
    )


    developmentstatus_choice=schema.Choice(
        title = _(u"Development Status"),
        source=vocabDevelopmentStatus,
        required=True
    )

    licenses_choice= schema.List(
        title=_(u'License of the uploaded file'),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailLicenses),
        constraint = isNotEmptyLicenseChoice,
        required=True,
    )


    compatibility_choice= schema.List(
        title=_(u"Compatible with versions of LibreOffice"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailVersions),
        constraint = isNotEmptyCompatibilityChoice,
        required=True,
    )



    form.mode(title_declaration_legal='display')
    title_declaration_legal=schema.TextLine(
        title=_(u""),
        required=False
    )

    form.mode(declaration_legal='display')
    form.primary('declaration_legal')
    declaration_legal = RichText(
        title=_(u""),
        required=False
    )

    accept_legal_declaration=schema.Bool(
        title=_(u"Accept the above legal disclaimer"),
        description=_(u"Please declare that you accept the above legal disclaimer"),
        required=True
    )

    contact_address2 = schema.ASCIILine(
        title=_(u"Contact email-address"),
        description=_(u"Contact email-address for the project."),
        required=False
    )

    source_code_inside = schema.Choice(
        title=_(u"Is the source code inside the extension?"),
        vocabulary=yesnochoice,
        required=True
    )

    link_to_source = schema.URI(
        title=_(u"Please fill in the Link (URL) to the Source Code"),
        required=False
    )


    file = NamedBlobFile(
        title=_(u"The first file you want to upload"),
        description=_(u"Please upload your file."),
        required=True,
    )



    platform_choice= schema.List(
        title=_(u" First uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    form.fieldset('fileset1',
        label=u"File Upload 1",
        fields=['file1', 'platform_choice1', 'file2', 'platform_choice2', 'file3', 'platform_choice3']
    )

    file1 = NamedBlobFile(
        title=_(u"The second file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )



    platform_choice1= schema.List(
        title=_(u"Second uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    file2 = NamedBlobFile(
        title=_(u"The third file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )



    platform_choice2= schema.List(
        title=_(u"Third uploaded file is compatible with the Platform(s))"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    file3 = NamedBlobFile(
        title=_(u"The fourth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )

    platform_choice3= schema.List(
        title=_(u"Fourth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    form.fieldset('fileset2',
        label=u"File Upload 2",
        fields=['file4', 'platform_choice4', 'file5', 'platform_choice5']
    )

    file4 = NamedBlobFile(
        title=_(u"The fifth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )


    platform_choice4= schema.List(
        title=_(u"Fifth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )

    file5 = NamedBlobFile(
        title=_(u"The sixth file you want to upload (this is optional)"),
        description=_(u"Please upload your file."),
        required=False,
    )

    platform_choice5= schema.List(
        title=_(u"Sixth uploaded file is compatible with the Platform(s)"),
        description=_(u"Please mark one or using the 'CTRL' key two and more entry on the left side and use the arrows in the middle to choose them and get them into the selected items box on the right side."),
        value_type=schema.Choice(source=vocabAvailPlatforms),
        required=True,
    )


    @invariant
    def licensenotchoosen(value):
        if value.licenses_choice == []:
            raise Invalid(_(u"Please choose a license for your release."))

    @invariant
    def compatibilitynotchoosen(data):
        if data.compatibility_choice == []:
            raise Invalid(_(u"Please choose one or more compatible product versions for your release"))

    @invariant
    def legaldeclarationaccepted(data):
        if data.accept_legal_declaration is not True:
           raise AcceptLegalDeclaration(_(u"Please accept the Legal Declaration about your Release and your Uploaded File"))

    @invariant
    def testingvalue(data):
        if data.source_code_inside is not 1 and data.link_to_source is None:
            raise Invalid(_(u"Please fill in the Link (URL) to the Source Code."))

    @invariant
    def noOSChosen(data):
        if data.file is not None and data.platform_choice ==[]:
            raise Invalid(_(u"Please choose a compatible platform for the uploaded file."))



@form.default_value(field=IEUpRelease['declaration_legal'])
def LegalTextDefaultValue(data):
    # To get hold of the folder, do: context = data.context
    return data.context.__parent__.legal_disclaimer

@form.default_value(field=IEUpRelease['title_declaration_legal'])
def legal_declaration_title_default(data):
    # To get hold of the folder, do: context = data.context
    return data.context.aq_inner.aq_parent.title_legaldisclaimer

@form.default_value(field=IEUpRelease['contact_address2'])
def contactinfoDefaultValue(data):
    return data.context.contactAddress



#View
class View(dexterity.DisplayForm):
    grok.context(IEUpRelease)
    grok.require('zope2.View')

    def canPublishContent(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)



