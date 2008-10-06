from zope.interface import Interface, Attribute

class IXml(Interface):
    def serialize(element, settings, url):
        """Serialize object structure into lxml element.

        element - an lxml element
        settings - an object influencing the export
        url - the url under which this can be addressed

        Returns the newly created sub-element
        """

    def serialize_compact(element, settings, url):
        """Serialize object structure to lxml element, compactly.

        Compactness means that not all levels of nesting may be
        serialized. This implementation may be identical to that of
        serialize(), however.
        """
        
    def factory(element):
        """Create a new sub-object based on XML.
        
        Raises a ValueError if this is not possible.

        Returns the newly created object.
        """

    def replace(element):
        """Replace content of object with that in element.

        Raise a ValueError if this is not possible.
        """

class IXmlFactory(Interface):
    def create(context, element, is_allowed):
        """Read XML and read it into context.

        context - object to create object inside
        element - element describing the object
        is_allowed - function that can be called with a newly created
                     object and that determines whether this object may
                     be added to the context.

        Returns the newly created object.
        """

    def replace(element, result):
        """Read in XML and replace result with contents.
        """

class IImageStore(Interface):
    pass

class ISession(Interface):
    pass

class IPathIndexable(Interface):
    paths = Attribute('All possible paths to this object')
     
class IRest(Interface):
    """An object that can be represented as XML and answer GET and PUT.

    Potentially POST and DELETE as well.
    """

class IHTTPEmbed(Interface):
    """Determine whether HTTP status should be embedded in the XML response.
    """

    def __call__():
        """Return True if HTTP status should be embedded.
        """

class IHTTPOnly200(Interface):
    """Determine whether the client is expected to return anything but
    200 response codes.
    """

    def __call__(self, request):
        """Return True if only 200 is accepted.

        The request object may be sniffed to make this determination.
        """

