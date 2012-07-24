#/usr/bin/python
""" $Id: KIFSyntax.py,v 1.3 2001/12/20 15:33:27 connolly Exp $
main function is quoterm

cf

[KIF] 
     Knowledge Interchange Format draft proposed American National Standard (dpANS)
     NCITS.T2/98-004
     Last Modified: Thursday, 25-Jun-98 22:31:37 GMT 

http://logic.stanford.edu/kif/dpans.html
"""


import re



"""4.2 Characters"""

upper="[A-Z]"
lower="[a-z]"
digit="[0-9]"
alpha=r"[\!\$\%\&\*\+\-\.\/\<\=\>\?\@\_\~\:]" #@@colon: use for namespaces
special=r"[\"\#\'\(\)\,\\\^\`]"
white=r"[ \t\r\n\f]"
normal=r"(?:%s|%s|%s|%s)" % (upper, lower, digit, alpha)

"""4.3 Lexemes"""

word = r"(?:%s(?:%s|\\.)*)" % (normal, normal)

charref = r"(?:#\\.)" # using . for character; @@BUG? missing newlines?

strchar = r"[^\"\\]"
quotable = r"(?:(?:%s|(?:\\.))*)" % (strchar,)
string = r"(?:\"(?P<quotable>%s)\")" % (quotable,)

blockMark = r"(?:#(\d+)[qQ])"

atom = r"%s*(?:(?P<word>%s)|(?P<charref>%s)|(?P<string>%s)|(?P<blockMark>%s))" % \
       (white, word, charref, string, blockMark)

atomFSM = re.compile(atom)

listMarkFSM = re.compile(r"\s*\(")
listEndFSM = re.compile(r"\s*\)")
quotermMarkFSM = re.compile(r"\s*'")

W_quote = 'quote' #@@sym/string???

class BadSyntax:
    def __init__(self, offending):
        self._o = offending
    def __str__(self):
        return "at: " + self._o
    
    pass #@@ flesh out


def identity(x): return x

# allocate distinct thingamabobs for these...
ListEnd = ('ListEnd',)
Dot = ('Dot',)

def quoterm(str, pos=0, endpos=-1, symNamed=identity):
    """ return a python tuple representing the KIF form in str.
    @@hmm... strings, symbols, and characters are indistinguishable.
    Also: strings aren't unescaped.
    """
    if endpos==-1: endpos=len(str)

    qt, w = _quoterm(str, pos, endpos, symNamed)
    #@@ what to do if w isn't at the end?

    return qt

def _quoterm(str, pos, endpos, symNamed):
    """ return (t, i) where t is the python representation of the quoterm,
    and i is the index of the next character after the term in str.
    return (None, i) for )."""

    m = atomFSM.match(str, pos, endpos)
    if m:
	w = m.group('word')

	if w == '.': return (Dot, m.end()) #@@not KIF!

	if w: return (symNamed(w), m.end()) #@@hmm... how to distinguish strings from words?

	c = m.group('charref')
	if c: return (c[2], m.end()) #@@hmm... how to distinguish characters from strings?

	s = m.group('string')
	if s: return (m.group('quotable'), m.end()) #@@hmm... unescape \char stuff

	b = m.group('blockMark')
	if b: raise RuntimeError, 'blocks not implemented yet'

	raise RuntimeError, 'matched none of the options???'

    l = listMarkFSM.match(str, pos, endpos)
    if l:
	res = [()] #@@HACK! list end object kept at 0th item
	at = l.end()
	while 1:
	    #print "_quoterm recur after (:", str[at:endpos]
	    qt = _quoterm(str, at, endpos, symNamed)
	    t, at = qt
	    if t == ListEnd: break
	    if t == Dot:
		qt = _quoterm(str, at, endpos, symNamed)
		t, at = qt
		if type(t) is type((1,)):
		    res.extend(list(t[1:]))
		else:
		    res[0] = t
		qt = _quoterm(str, at, endpos, symNamed)
		t, at = qt
                if t <> ListEnd: raise BadSyntax, t[at:at+20]
		break
	    res.append(t)

	if len(res) == 1: res = ()
	else: res = tuple(res)

	return (res, at)

    e = listEndFSM.match(str, pos, endpos)
    if e:
	return (ListEnd, e.end())

    q = quotermMarkFSM.match(str, pos, endpos)
    if q:
	print "_quoterm recur after ':", str[at:endpos]
	py, at = _quoterm(str, q.end(), endpos)
	return ((W_quote, py), at)

    raise BadSyntax, str[pos:pos+30]

def unitTest():
    print "atom RE:", atom

    cases = (r"1",
	     r"(1 2 3)",
	     r" (1 2 3)",
	     r">",
	     r"=>",
	     r"foo:bar",
	     r" >",
	     r"?x",
	     r"abc",
	     r" abc",
	     r"#\a",
	     r" #\a",
	     "\"abcdef\"",
	     " \"abcdef\"",
	     "\"abc\def\"",
	     "\"\"",
	     """ "abc\\\"def" """,
	     r"()",
	     r"(())",
	     r"(() a b c (29 adf))",
	     r"(< ?y ?x)",
	     """
	     (forall (?p)
	       (<=> (rdf-type ?p daml-TransitiveProperty)
	         (forall (?x ?y ?z)
		  (=> (and (?p ?x ?y) (?p ?y ?z)) (?p ?x ?z))
		  ) ) )
	     """
	     r")))",
	     )

    for c in cases:
	print "== in:", c
	o = quoterm(c)
	print "out: ", o

    
if __name__ == '__main__': unitTest()
