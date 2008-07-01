import sys
import urllib2
import httplib
from urlparse import urlparse
import os
import glob
import time

from frontend.rest import Rest, NS

def main():
    try:
        backend_url = sys.argv[1]
        session = sys.argv[2]
        group = sys.argv[3]
        image_path = sys.argv[4]
    except IndexError:
        print "Usage: filler <backend_url> <session> <group> <image_file>"
        print "       filler <backend_url> <session> <group> <image_dir>"
        return

    backend_rest = Rest(backend_url)

    sessions_rest = backend_rest.click_to(
        'ids:sessions/@href')
    
    # look for session
    session_url = sessions_rest.url_to(
        'ids:session[@name="%s"]/@href' % session)
    
    if session_url is None:
        # create session
        xml = '''
        <session xmlns="http://studiolab.io.tudelft.nl/ns/imagestore" name="%s">
        </session>
        ''' % session
        sessions_rest.post(xml)
        # XXX should get real URL of newly created object somehow..
        session_url = sessions_rest.url_to(
            'ids:session[@name="%s"]/@href' % session)
    session_rest = Rest(session_url)

    # now add/update images
    images_rest = session_rest.click_to('ids:images/@href')

    # existing images
    image_elements = images_rest.xpath('ids:source-image')
    images = {}
    for image_element in image_elements:
        images[image_element.get('name')] = (
            images_rest.url + '/' + image_element.get('href'))

    # new images
    image_files = find_images(image_path)

    # now add/replace images where necessary
    added_images = []
    for image_name, image_path in image_files.items():
        print "adding:", image_path
        f = open(image_path, 'rb')
        data = f.read()
        f.close()
        if image_name in images:
            image_rest = Rest(images[image_name])
            image_rest.put(data)
            added_images.append(image_name)
        else:
            images_rest.post(data, Slug=image_name)
            # XXX should get this from Location header in post somehow?
            added_images.append(image_name)
        time.sleep(0.1)

    root_objects_rest = session_rest.click_to('ids:group/ids:objects/@href')

    # get group if it exists
    group_url = root_objects_rest.url_to('ids:group[@name="%s"]/@href' % group)
    if group_url is None:
        # create group if it doesn't exist
        xml = '''
        <group xmlns="http://studiolab.io.tudelft.nl/ns/imagestore" name="%s">
          <source name="UNKNOWN" />
          <metadata>
            <depth>0</depth>
            <rotation>0</rotation>
            <x>0</x>
            <y>0</y>
          </metadata>
          <objects />
        </group>
        ''' % group 
        response = root_objects_rest.post(xml)
        group_url = root_objects_rest.url_to('ids:group[@name="%s"]/@href' %
                                             group)
    group_rest = Rest(group_url)

    objects_rest = group_rest.click_to('ids:objects/@href')
    
    # now add images as objects to group
    i = 0
    for image_name in added_images:
        xml = '''
        <image xmlns="http://studiolab.io.tudelft.nl/ns/imagestore" name="%s">
          <source name="%s" />
          <metadata>
            <depth>0</depth>
            <rotation>0</rotation>
            <x>0</x>
            <y>0</y>
          </metadata>
        </image>
        ''' % (str(i), image_name)
        objects_rest.post(xml)
        i += 1
        time.sleep(0.1)

def find_images(image_path):
    # a single image
    if os.path.isfile(image_path):
        return { os.path.basename(image_path): image_path}

    # a directory, scan it for images
    images = []
    for ext in ['gif', 'png', 'jpg']:
        for variant_ext in [ext.lower(), ext.upper()]:
            images += glob.glob(os.path.join(image_path, '*.%s' % variant_ext))
    result = {}
    for path in images:
        result[os.path.basename(path)] = path
    return result

if __name__ == '__main__':
    main()
