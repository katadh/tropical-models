# extract all categories from a wiki dump, e.g. from https://en.wikipedia.org/wiki/Special:Export
# track articles they come from
# and count em

fn = "/Users/kristen/Box Sync/Semantics/Wikipedia-20170407184627.xml"

def scan_file(fn, cat_dict):
	with open(fn) as f:
		on_art_id = False
		for line in f:
			if line == "  <page>\n": #track whether we're on first ID in a new page
				on_art_id = True
				#print "saw a page tag; set on_art_id to True"
			elif on_art_id and line.split('>')[0] == '    <id':
				curr_id = line.split('>')[1].split('<')[0]
				on_art_id = False #revision IDs will start coming up; ignore those
				#print "just set curr_id to", curr_id
			elif line.split(':')[0] == "[[Category":
				cat=line.split(':')[1].split(']')[0]
				if '|' in cat:
					cat = cat.split('|')[0]
				if cat in cat_dict:
					cat_dict[cat].append(curr_id)
				else:
					cat_dict[cat] = [curr_id]
					#print "added %s to dict" % cat

def handler(files = [fn]):
	cat_dict = dict()
	for filename in files:
		scan_file(filename, cat_dict)
	#print cat_dict

	biggest = 0
	big_cat = None
	for key in cat_dict:
		if len(cat_dict[key]) > biggest:
			biggest = len(cat_dict[key])
			big_cat = key
	print "the biggest category is %s with %d items" % (big_cat, biggest)

	return cat_dict

if __name__ == "__main__": 
	handler()