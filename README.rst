============
xmlformatter
============

`xmlformatter <http://pamoller.com/xmlformatter.html>`_ is an Open Source Python package, which provides formatting of XML documents. *It is the replacement for the Python 2 package XmlFormatter, which has been removed from PyPi completely (see Notes)*. xmlformatter differs from others formatters by *handling whitespaces by a distinct set of formatting rules* - formatting element content by a object style and mixed content by a text style. You may find xmlformatter useful for corrections and presentations. In addition xmlformatter comes with a wrapper script named xmlformat.

================
Formatting Rules
================

xmlformatter treats the element content from the following example as a object. The elements are associated with containers, like complex, or properties names, like real and imaginary. Text nodes are associated with property values, like 4.4E+12. Leading and trailing whitespaces are meaningless in this scenario like sequences of whitespaces. Leading and trailing whitespaces will be remove, sequences of whitespaces will be collapsed.

::

    <complex>
      <real>  4.4E+12</real>
     <imaginary>5.4E-11
       </imaginary>
    </complex>

The element content from the example above can be formatted by xmlformat:

::

    $ xmlformat ele.xml

The following output shows the formatted XML document. xmlformatter has removed leading and trailing whitespaces from the text nodes and has indented the child elements equal. This formatting style is called object style.

::

    <complex>
      <real>4.4E+12</real>
      <imaginary>5.4E-11</imaginary>
    </complex>

xmlformatter treats the mixed content from the following example as a literal text with some markup. The outer element enclose poem encloses the text. The inline element em gives a text snippet a special meaning. Leading and trailing whitespaces enclosed by inline elements are misplaced. They will be adopted by the previous or following text node. Note: xmlformatter may insert a text node if necessary. Even sequences of whitespaces will be collapsed:

::

    <poem> Es<em>   war</em> einmal und <em>ist  </em>nicht mehr...</poem>

The following output shows the formatted XML document. xmlfromatter has removed leading and trailing whitespaces and has collapsed sequences of whitespaces. This formatting style is called text style.

::

    <poem>Es <em>war</em> einmal und <em>ist</em> nicht mehr...</poem>

Both styles are used while formatting a XML document. The formatting rules are:    

A: Surrounding whitespaces are removed from element content.    

B: Leading whitespaces are removed from element content.    

C: Trailing whitespaces are removed from element content.    

D: Leading whitespaces of inline elements are put to preceding text (or inserted) if necessary within mixed content.    

E: Trailing whitespaces of inline elements are put to following text (or inserted) if necessary within mixed content.    

F: Sequences of whitespaces (n>2) are replaced by a single blank " " within element and mixed content.    

G: Linebreak and whitespace are used to indent elements within elements content.

The following example shows the described whitespaces by their labels within a XML document:

::

    <root>AAAA
    AAAA<number>BBBB4.4E+12CCC</number>AAAA
    AAAA<poem>BBBBEs<em>DDDDwar</em> einmal und <em>istEEEE</em>nicht mehrF
    FFFFein <strong>riesengroßer</strong><em>DDDDTeddybär</em>,F 
    der aßFFFFdie <em>MilchEEEE</em>und trank das BrotFFFF
    und als er starb da <strong>war erEEEE</strong><em>tot</em>.CCCC</poem>AAAA
    </root>

The following output shows the formatted XML document:

::

    <root>
        <number>4.4E+12</number>
        <poem>Es <em>war</em> einmal und <em>ist</em> nicht mehr ein <strong>riesengroßer</strong> <em>Teddybär</em>, der aß die <em>Milch</em>und trank das Brot und als er starb da <strong>war er</strong> <em>tot</em>.</poem>
    </root>

=====
Class
=====

::

    class xmlformatter.Formatter(compress ::= False, selfclose ::= False, indent ::= 2, indent_char ::= " ", inline ::= True, encoding_input ::= None, encoding_output ::= None, preserve ::= [ ], blanks ::= False)

The Formatter class can be used to format XML documents in scripts. By default all parts of the XML document will formatted. All descendants of elements listed by preserve are left unformatted. Setting the boolean property compress to True suppresses the indenting given by the indent and indent_char properties. Without a value given to encoding_input xmlformatter trys to determine the encoding from the XML document. On failure it use UTF-8 as default. encoding_output advises xmlformatter to encode the output explicit by the given value. Otherwise xmlformatter use the inpurt encoding. Setting the boolean property inline to False suppresses inline formatting. By default element content will be formatted everywhere - also within mixed content. The following example shows the usage of the xmlfromatter class:

::

    import xmlformatter
    
    formatter = xmlformatter.Formatter(indent="1", indent_char="\t", encoding_output="ISO-8859-1", preserve=["literal"])
    formatter.format_file("/home/pa/doc.xml")

The example formats the XML document in /home/pa/doc.xml, preserving the element literal, indenting by the tab character and output in ISO-8859-1 encoding.

=======
Members
=======

::

    compress ::= False

Minify the XML document.

::

    selfclose ::= False

Collapse ``<element></element>`` to ``<element/>``.

::

    correct ::= True

Apply formatting rules to whitespaces.

::

    indent ::= 2

Indent a child element in element content n-times by indent_char.

::

    indent_char ::= " "

Indent a child element by this string.

::

    input_encoding ::= None

Assume the XML document encoded by a not None value.

::

    output_encoding ::= None

Encode the formatted XML document by a not None value.

::

    preserve ::= [ ]

Skip formatting for all elements listed in preserve and all their descendants.

::

    blanks ::= False

Keep blank lines. Multiple lines are collapsed into one.

::

    eof_newline ::= False

Add a single newline character at the end of each file

=======
Methods
=======

::

     format_file(path)

Format a XML document given by a path.

::

     format_string(xmldoc)

Format a XML document given by a string.

===
Cmd
===

::

    xmlformat [--preserve "pre,literal"] [--blanks] [--compress] [--selfclose] [--indent num] [--indent-char char]
              [--overwrite] [--outfile file] [--encoding enc] [--outencoding enc] [--disable-inlineformatting] 
              [--dispable-correction] [--help] < --infile file | file | - >

xmlformat can read from STDIN, like:

::

    $ cat /home/pa/doc.xml | xmlformat -

Use --overwrite for inplace edits, see https://pre-commit.com/

=====
Notes
=====

Remove XmlFormatter before installing xmlformatter:

::

    $ pip uninstall XmlFormatter

After reinstallation replace the string "formatter.formatter" by "formatter", "preserving" by "preserve" and "indentChar" by "indent_char" inside your scripts carefully. To reach compatibility with XmlFormatter call xmlformat with --disable-inlineformatting or use inline=False in your scripts.
