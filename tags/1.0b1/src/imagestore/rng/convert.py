import os
import glob

for path in glob.glob('*.rnc'):
    name, ext = os.path.splitext(path)
    os.system('trang %s.rnc %s.rng' % (name, name))
