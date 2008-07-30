from datetime import datetime

import grok
from grok import index

from zope.traversing.interfaces import IPhysicallyLocatable

from imagestore.metadata import Metadata
from imagestore.source import Source
from imagestore.interfaces import IRest, IImageStore, IPathIndexable

class Object(grok.Container):
    grok.implements(IRest)
    
    def __init__(self, image_name):
        super(Object, self).__init__()
        self._image_name = image_name
        
    @property
    def tags(self):
        try:
            return self['metadata']['tags'].value
        except KeyError:
            return set()

    @property
    def created(self):
        try:
            return self['metadata']['created'].value
        except KeyError:
            return None

    @property
    def modified(self):
        try:
            return self['metadata']['modified'].value
        except KeyError:
            return None
        
    
class Tag(grok.View):
    def update(self, tags=None):
        if tags is None:
            return
        tags = set(tags.split(' '))
        self.context['metadata']['tags'].value = tags
        grok.notify(grok.ObjectModifiedEvent(self.context))

@grok.subscribe(Object, grok.IObjectAddedEvent)
def object_added(obj, event):
    obj['source'] = Source(obj._image_name)
    obj['metadata'] = Metadata()

@grok.subscribe(Object, grok.IObjectModifiedEvent)
def object_modified(obj, event):
    try:
        metadata = obj['metadata']
    except KeyError:
        return
    metadata['modified'].value = datetime.now()
    
class MetadataIndexes(grok.Indexes):
    grok.site(IImageStore)
    grok.context(Object)

    tags = index.Set()
    created = index.Field()
    modified = index.Field()

class PathIndexes(grok.Indexes):
    grok.site(IImageStore)
    grok.context(IPathIndexable)

    paths = index.Set()

class PathIndexable(grok.Adapter):
    grok.context(Object)
    grok.provides(IPathIndexable)

    def __init__(self, context):
        super(PathIndexable, self).__init__(context)
        physical_path = IPhysicallyLocatable(context).getPath()
        steps = physical_path.split('/')
        paths = []
        for i in range(1, len(steps) + 1):
            paths.append('/'.join(steps[:i]))
        self.paths = paths
