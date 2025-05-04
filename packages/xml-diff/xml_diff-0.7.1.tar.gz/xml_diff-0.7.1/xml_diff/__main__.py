import sys
import lxml.etree
from xml_diff import compare

# make an alias for Py3
if sys.version_info >= (3,):
  unicode = str

if len(sys.argv) < 3:
  print("Usage: python3 xml_diff.py [--tags del,ins] [--merge] before.xml after.xml")
  sys.exit(1)

tags = ['del', 'ins']
merge = False
kwargs = { }

args = sys.argv[1:]
while len(args) > 0:
  if args[0] == "--tags":
    args.pop(0)
    tags = args.pop(0).split(",")
  elif args[0] == "--merge":
    args.pop(0)
    merge = True
  elif args[0] == "--chars":
    args.pop(0)
    kwargs["word_separator_regex"] = None
  else:
    break

# Load the documents and munge them in-place.
dom1 = lxml.etree.parse(args[0]).getroot()
dom2 = lxml.etree.parse(args[1]).getroot()
compare(dom1, dom2, tags=tags, merge=merge, **kwargs)

# Output changed documents.
print(lxml.etree.tostring(dom1, encoding=unicode))
print(lxml.etree.tostring(dom2, encoding=unicode))
