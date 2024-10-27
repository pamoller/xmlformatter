"""
Format and compress XML documents 
"""
import getopt
import re
import sys
import xml.parsers.expat
import html

__version__ = "0.2.8"

DEFAULT_BLANKS = False
DEFAULT_COMPRESS = False
DEFAULT_SELFCLOSE = False
DEFAULT_CORRECT = True
DEFAULT_INDENT = 2
DEFAULT_INDENT_CHAR = " "
DEFAULT_INLINE = True
DEFAULT_ENCODING_INPUT = None
DEFAULT_ENCODING_OUTPUT = None
DEFAULT_EOF_NEWLINE = False
DEFAULT_PERSERVE_ATTRIBUTES = False
DEFAULT_ENCODE_ATTRIBUTES = False

class Formatter:
    # Use internal encoding:
    encoding_internal = None

    def __init__(
        self,
        indent=DEFAULT_INDENT,
        preserve=[],
        blanks=DEFAULT_BLANKS,
        compress=DEFAULT_COMPRESS,
        selfclose=DEFAULT_SELFCLOSE,
        indent_char=DEFAULT_INDENT_CHAR,
        encoding_input=DEFAULT_ENCODING_INPUT,
        encoding_output=DEFAULT_ENCODING_OUTPUT,
        inline=DEFAULT_INLINE,
        correct=DEFAULT_CORRECT,
        eof_newline=DEFAULT_EOF_NEWLINE,
        preserve_attributes=DEFAULT_PERSERVE_ATTRIBUTES,
        encode_attributes=DEFAULT_ENCODE_ATTRIBUTES,
    ):
        # Minify the XML document:
        self.compress = compress
        # Use self-closing tags
        self.selfclose = selfclose
        # Correct text nodes
        self.correct = correct
        # Decode the XML document:
        self.encoding_input = self.enc_normalize(encoding_input)
        # Encode ouput by:
        self.encoding_output = self.enc_normalize(encoding_output)
        # Insert indent = indent*level*indent_char:
        self.indent = int(indent)
        # Indent by char:
        self.indent_char = indent_char
        # Format inline objects:
        self.inline = inline
        # Don't compress this elements and their descendants:
        self.preserve = preserve
        # Preserve blanks lines (collapse multiple into one)
        self.blanks = blanks
        # Always add a newline character at EOF
        self.eof_newline = eof_newline
        # Preserve the order of attributes
        self.preserve_attributes = preserve_attributes
        # Decode entity references in attributes
        self.encode_attributes = encode_attributes

    @property
    def encoding_effective(self, enc=None):
        if self.encoding_output:
            return self.encoding_output
        elif self.encoding_internal:
            return self.encoding_internal
        elif self.encoding_input:
            return self.encoding_input
        else:
            return "UTF-8"

    def enc_normalize(self, string):
        """ Format an Encoding identifier to upper case. """
        if isinstance(string, str):
            return string.upper()
        return None

    def enc_encode(self, strg):
        """ Encode a formatted XML document in target"""
        if sys.version_info > (3, 0):
            return strg.encode(self.encoding_effective)  # v3
        return strg.decode("utf-8").encode(self.encoding_effective)  # v2

    def enc_output(self, path, strg):
        """ Output according to encoding """
        fh = sys.stdout
        if strg is not None:
            if path is not None:
                open(path, "w+b").write(strg)
            elif sys.version_info > (3, 0):
                fh.buffer.write(strg)
            else:
                fh.write(strg)

    def format_string(self, xmldoc=""):
        """ Format a XML document given by xmldoc """
        token_list = Formatter.TokenList(self)
        token_list.parser.Parse(xmldoc, True)
        return self.enc_encode(str(token_list))

    def format_file(self, file):
        """ Format a XML document given by path name """
        fh = open(file, "rb")
        token_list = Formatter.TokenList(self)
        token_list.parser.ParseFile(fh)
        fh.close()
        return self.enc_encode(str(token_list))

    class TokenList:
        # Being in a cdata section:
        cdata_section = False
        # Lock deletion of leading whitespace:
        desc_mixed_level = None
        # Lock indenting:
        indent_level = None
        # Reference the Formatter:
        formatter = None
        # Count levels:
        level_counter = 0
        # Lock deletion of whitespaces:
        preserve_level = None

        def __init__(self, formatter):
            # Keep tokens in a list:
            self._list = []
            self.formatter = formatter
            self.parser = xml.parsers.expat.ParserCreate(
                encoding=self.formatter.encoding_input
            )
            self.parser.specified_attributes = 1
            self.parser.buffer_text = True
            self.parser.SetParamEntityParsing(xml.parsers.expat.XML_PARAM_ENTITY_PARSING_NEVER)

            # Push tokens to buffer:
            for pattern in [
                "XmlDecl%s",
                "ElementDecl%s",
                "AttlistDecl%s",
                "EntityDecl%s",
                "StartElement%s",
                "EndElement%s",
                "ProcessingInstruction%s",
                "CharacterData%s",
                "Comment%s",
                "Default%s",
                "StartDoctypeDecl%s",
                "EndDoctypeDecl%s",
                "StartCdataSection%s",
                "EndCdataSection%s",
                "NotationDecl%s",
            ]:
                setattr(
                    self.parser, pattern % "Handler", self.xml_handler(pattern % "")
                )

        def __iter__(self):
            return iter(self._list)

        def __len__(self):
            return len(self._list)

        def __getitem__(self, pos):
            if 0 <= pos < len(self._list):
                return self._list[pos]
            else:
                raise IndexError

        def __setitem__(self, pos, value):
            if 0 <= pos < len(self._list):
                self._list[pos] = value
            else:
                raise IndexError

        def __str__(self):
            """ Returns the formatted XML document in UTF-8. """
            for step in ["configure", "pre_operate", "post_operate"]:
                for tk in iter(self):
                    getattr(tk, step)()
            result = ""
            for tk in iter(self):
                result += str(tk)
            if self.formatter.eof_newline and not result.endswith("\n"):
                result += "\n"
            return result

        def append(self, tk):
            """ Add token to tokenlist. """
            tk.pos = len(self._list)
            self._list.append(tk)

        def level_increment(self):
            """ Increment level counter. """
            self.level_counter += 1

        def level_decrement(self):
            """ Decrement level counter. """
            self.level_counter -= 1

        def token_descendant_mixed(self, tk):
            """ Mark descendants of mixed content. """
            if tk.name == "StartElement":
                # Mark every descendant:
                if tk.content_model in [2, 3] and self.desc_mixed_level is None:
                    self.desc_mixed_level = tk.level
                    return False
                return self.desc_mixed_level is not None
            elif tk.name == "EndElement":
                # Stop marking every descendant:
                if tk.level is self.desc_mixed_level:
                    self.desc_mixed_level = None
                elif self.desc_mixed_level is not None:
                    return True
                return False
            elif self.desc_mixed_level is None:
                return False
            return self.desc_mixed_level >= tk.level - 1

        def sequence(self, tk, scheme=None):
            """Returns sublist of token list.
            None: next to last
            EndElement: first to previous"""
            if scheme == "EndElement" or (scheme is None and tk.end):
                return reversed(self._list[: tk.pos])
            return self._list[(tk.pos + 1) :]

        def token_indent(self, tk):
            if self.formatter.inline:
                return self.token_indent_inline(tk)
            """ Indent outside of text of mixed content. """
            if tk.name == "StartElement":
                # Block indenting for descendants of text and mixed content:
                if tk.content_model in [2, 3] and self.indent_level is None:
                    self.indent_level = tk.level
                elif self.indent_level is not None:
                    return False
                return True
            elif tk.name == "EndElement":
                # Unblock indenting for descendants of text and mixed content:
                if tk.level == self.indent_level:
                    self.indent_level = None
                elif self.indent_level is None:
                    return True
                return False
            return self.indent_level is None

        def token_indent_inline(self, tk):
            """ Indent every element content - no matter enclosed by text or mixed content. """
            for itk in iter(self.sequence(tk, "EndElement")):
                if itk.level < tk.level and itk.name == "StartElement":
                    if itk.content_model == 1:
                        return True
                    return False
                if (
                    itk.level == tk.level
                    and tk.name == "EndElement"
                    and itk.name == "StartElement"
                ):
                    if itk.content_model == 1:
                        return True
                    return False
            return True

        def token_model(self, tk):
            """Returns code for content model.
            0: empty
            1: element
            2: text
            3: mixed"""
            eflag = tflag = 0
            for itk in iter(self.sequence(tk)):
                # Element boundary found:
                if itk.level <= tk.level:
                    break
                # Direct child found:
                elif (itk.level - 1) == tk.level:
                    if itk.start:
                        eflag = 1
                    elif itk.not_empty:
                        tflag = 2
            return eflag + tflag

        def token_preserve(self, tk):
            """Preseve eyery descendant of an preserved element.
            0: not locked
            1: just (un)locked
            2: locked"""
            # Lock perserving for StartElements:
            if tk.name == "StartElement":
                if self.preserve_level is not None:
                    return 2
                if tk.arg[0] in self.formatter.preserve:
                    self.preserve_level = tk.level
                    return 1
                return 0
            # Unlock preserving for EndElements:
            elif tk.name == "EndElement":
                if (
                    tk.arg[0] in self.formatter.preserve
                    and tk.level == self.preserve_level
                ):
                    self.preserve_level = None
                    return 1
                elif self.preserve_level is None:
                    return 0
                return 2
            return self.preserve_level is not None

        def whitespace_append_trailing(self, tk):
            """ Add a trailing whitespace to previous character data. """
            if self.formatter.correct and tk.leading and tk.not_empty:
                self.whitespace_append(tk, "EndElement", "StartElement", True)

        def whitespace_append_leading(self, tk):
            """ Add a leading whitespace to previous character data. """
            if self.formatter.correct and tk.trailing and tk.not_empty:
                self.whitespace_append(tk)

        def whitespace_append(
            self, tk, start="StartElement", stop="EndElement", direct=False
        ):
            """ Add a whitspace to token list. """
            for itk in self.sequence(tk, start):
                if (
                    itk.empty
                    or (itk.name == stop and itk.descendant_mixed is False)
                    or (itk.name == start and abs(tk - itk) == 1)
                ):
                    break
                elif itk.not_empty or (itk.name == start and itk.descendant_mixed):
                    self.insert_empty(itk, direct)
                    break

        def whitespace_delete_leading(self, tk):
            """ Returns True, if no next token or all empty (up to next end element)"""
            if (
                self.formatter.correct
                and tk.leading
                and not tk.preserve
                and not tk.cdata_section
            ):
                for itk in self.sequence(tk, "EndElement"):
                    if itk.trailing:
                        return True
                    elif itk.name in ["EndElement", "CharacterData", "EndCdataSection"]:
                        return False
                return True
            return False

        def whitespace_delete_trailing(self, tk):
            """Returns True, if no next token or all empty (up to next end element)"""
            if (
                self.formatter.correct
                and tk.trailing
                and not tk.preserve
                and not tk.cdata_section
            ):
                for itk in self.sequence(tk, "StartElement"):
                    if itk.end:
                        return True
                    elif (
                        itk.name in ["StartElement", "StartCdataSection"]
                        or itk.not_empty
                    ):
                        return False
                return True
            return False

        def insert_empty(self, tk, before=True):
            """ Insert an Empty Token into token list - before or after tk. """
            if not (0 < tk.pos < (len(self) - 1)):
                return False
            ptk = self[tk.pos - 1]
            ntk = self.formatter.CharacterData(self, [" "])
            ntk.level = max(ptk.level, tk.level)
            ntk.descendant_mixed = tk.descendant_mixed
            ntk.preserve = ptk.preserve * tk.preserve
            ntk.cdata_section = ptk.cdata_section or tk.cdata_section
            if before:
                self._list.insert(tk.pos + 1, ntk)
            else:
                self._list.insert(tk.pos, ntk)
            for i in range((tk.pos - 1), len(self._list)):
                self._list[i].pos = i

        def xml_handler(self, key):
            """ Returns lambda function which adds token to token list"""
            return lambda *arg: self.append(getattr(self.formatter, key)(self, arg))

    class Token(object):
        def __init__(self, tklist, arg):
            # Reference Token List:
            self.list = tklist
            # Token datas:
            self.arg = list(arg)
            # Token is placed in an CDATA section:
            self.cdata_section = False
            # Token has content model:
            self.content_model = None
            # Remove trailing wihtespaces:
            self.delete_trailing = False
            # Remove leading whitespaces:
            self.delete_leading = False
            # Token is descendant of text or mixed content element:
            self.descendant_mixed = False
            # Reference to formatter:
            self.formatter = tklist.formatter
            # Insert indenting white spaces:
            self.indent = False
            # N-th generation of roots descendants:
            self.level = self.list.level_counter
            # Token class:
            self.name = self.__class__.__name__
            # Preserve white spaces within enclosed tokens:
            self.preserve = False
            # Position in token list:
            self.pos = None

        def __sub__(self, other):
            return self.pos - other.pos

        def __unicode__(self):
            return ""

        # Workaround, see http://lucumr.pocoo.org/2011/1/22/forwards-compatible-python/:
        if sys.version_info > (3, 0):
            __str__ = lambda x: x.__unicode__()
        else:
            __str__ = lambda x: unicode(x).encode("utf-8")

        @property
        def end(self):
            return self.name == "EndElement"

        @property
        def empty(self):
            return self.name == "CharacterData" and re.match(
                r"^[\t\s\n]*$", self.arg[0]
            )

        @property
        def leading(self):
            return self.name == "CharacterData" and re.search(
                r"^[\t\s\n]+", self.arg[0]
            )

        @property
        def not_empty(self):
            return (
                self.name == "CharacterData"
                and not self.cdata_section
                and not re.match(r"^[\t\s\n]+$", self.arg[0])
            )

        @property
        def trailing(self):
            return self.name == "CharacterData" and re.search(
                r"[\t\s\n]+$", self.arg[0]
            )

        @property
        def start(self):
            return self.name == "StartElement"

        @property
        def correct(self):
            return self.formatter.correct

        def attribute(self, key, value):
            if key and value:
                if not self.formatter.encode_attributes:
                    return ' %s="%s"' % (key, value.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;'))
                else:
                    return ' %s="%s"' % (key, value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", "&apos;"))  
                
            elif key:
                return ' %s=""' % (key)
            return ""

        def indent_insert(self):
            """ Indent token. """
            # Child of root and no empty node
            if (
                self.level > 0 and not (self.end and self.list[self.pos - 1].start)
            ) or (  # not empty node:
                self.end and not self.list[self.pos - 1].start
            ):
                return self.indent_create(self.level)
            return ""

        def indent_create(self, times=1):
            """ Returns indent string. """
            if not self.formatter.compress and self.formatter.indent:
                return "\n%s" % (
                    (times * self.formatter.indent) * self.formatter.indent_char
                )
            return ""

        def identifier(self, systemid, publicid):
            # TODO add base parameter:
            if publicid and systemid:
                return ' PUBLIC "%s" "%s"' % (publicid, systemid)
            elif publicid:
                return ' PUBLIC "%s"' % publicid
            elif systemid:
                return ' SYSTEM "%s"' % systemid
            return ""

        def configure(self):
            """ Set token properties. """
            self.descendant_mixed = self.list.token_descendant_mixed(self)
            self.preserve = self.list.token_preserve(self)
            self.cdata_section = self.list.cdata_section

        def pre_operate(self):
            pass

        def post_operate(self):
            pass

    class AttlistDecl(Token):
        def __unicode__(self):
            str = self.indent_create()
            str += "<!ATTLIST %s %s" % (self.arg[0], self.arg[1])
            if self.arg[2] is not None:
                str += " %s" % self.arg[2]
            if self.arg[4] and not self.arg[3]:
                str += " #REQUIRED"
            elif self.arg[3] and self.arg[4]:
                str += " #FIXED"
            elif not self.arg[4] and not self.arg[3]:
                str += " #IMPLIED"
            if self.arg[3]:
                str += ' "%s"' % self.arg[3]
            str += ">"
            return str

    class CharacterData(Token):
        def __unicode__(self):
            str = self.arg[0]
            if not self.preserve and not self.cdata_section:
                # remove empty tokens always in element content!
                if self.empty and not self.descendant_mixed:
                    if self.formatter.blanks and not self.formatter.compress and re.match(r"\s*\n\s*\n\s*", str):
                        str = "\n"
                    else:
                        str = ""
                else:
                    if self.correct:
                        str = re.sub(r"\r\n", "\n", str)
                        str = re.sub(r"\r|\n|\t", " ", str)
                        str = re.sub(r"\s+", " ", str)
                    if self.delete_leading:
                        str = re.sub(r"^\s", "", str)
                    if self.delete_trailing:
                        str = re.sub(r"\s$", "", str)
            if not self.cdata_section:
                str = re.sub(r"&", "&amp;", str)
                str = re.sub(r"<", "&lt;", str)
            return str

        def pre_operate(self):
            self.list.whitespace_append_trailing(self)
            self.list.whitespace_append_leading(self)

        def post_operate(self):
            self.delete_leading = self.list.whitespace_delete_leading(self)
            self.delete_trailing = self.list.whitespace_delete_trailing(self)

    class Comment(Token):
        def __unicode__(self):
            str = ""
            if self.preserve in [0, 1] and self.indent:
                str += self.indent_insert()
            str += "<!--%s-->" % re.sub(
                r"^[\r\n]+$", "\n", re.sub(r"^[\r\n]+", "\n", self.arg[0])
            )
            return str

        def configure(self):
            super(Formatter.Comment, self).configure()
            self.indent = self.list.token_indent(self)

    class Default(Token):
        pass

    class EndCdataSection(Token):
        def __unicode__(self):
            return "]]>"

        def configure(self):
            self.list.cdata_section = False

    class ElementDecl(Token):
        def __unicode__(self):
            str = self.indent_create()
            str += "<!ELEMENT %s%s>" % (self.arg[0], self.evaluate_model(self.arg[1]))
            return str

        def evaluate_model(self, model, modelStr="", concatStr=""):
            childSeq = []
            mixed = model[0] == xml.parsers.expat.model.XML_CTYPE_MIXED
            hasChilds = len(model[3]) or mixed
            if model[0] == xml.parsers.expat.model.XML_CTYPE_EMPTY:  # 1
                modelStr += " EMPTY"
            elif model[0] == xml.parsers.expat.model.XML_CTYPE_ANY:  # 2
                modelStr += " ANY"
            elif model[0] == xml.parsers.expat.model.XML_CTYPE_NAME:  # 4
                modelStr = "%s" % model[2]  # new start
            elif model[0] in (
                xml.parsers.expat.model.XML_CTYPE_CHOICE,
                xml.parsers.expat.model.XML_CTYPE_MIXED,
            ):  # 5
                concatStr = "|"
            elif model[0] == xml.parsers.expat.model.XML_CTYPE_SEQ:  # 6
                concatStr = ","
            if hasChilds:
                modelStr += " ("
            if mixed:
                childSeq.append("#PCDATA")
            for child in model[3]:
                childSeq.append(self.evaluate_model(child))
            modelStr += concatStr.join(childSeq)
            if hasChilds:
                modelStr += ")"
            modelStr += {
                xml.parsers.expat.model.XML_CQUANT_NONE: "",
                xml.parsers.expat.model.XML_CQUANT_OPT: "?",
                xml.parsers.expat.model.XML_CQUANT_PLUS: "+",
                xml.parsers.expat.model.XML_CQUANT_REP: "*",
            }[model[1]]
            return modelStr

    class EndDoctypeDecl(Token):
        def __unicode__(self):
            str = ""
            if self.list[self.pos - 1].name != "StartDoctypeDecl":
                str += self.indent_create(0)
                str += "]"
            str += ">"
            str += self.indent_create(0)
            return str

    class EndElement(Token):
        def __init__(self, list, arg):
            list.level_decrement()
            super(Formatter.EndElement, self).__init__(list, arg)

        def __unicode__(self):
            str = ""
            # Don't close empty nodes on compression mode:
            if (
                not (self.formatter.compress or self.formatter.selfclose)
                or self.list[self.pos - 1].name != "StartElement"
            ):
                if self.preserve in [0] and self.indent:
                    str += self.indent_insert()
                str += "</%s>" % self.arg[0]
            return str

        def configure(self):
            self.descendant_mixed = self.list.token_descendant_mixed(self)
            self.preserve = self.list.token_preserve(self)
            self.indent = self.list.token_indent(self)

    class EntityDecl(Token):
        def __unicode__(self):
            str = self.indent_create()
            str += "<!ENTITY "
            if self.arg[1]:
                str += "% "
            str += "%s " % self.arg[0]
            if self.arg[2]:
                str += '"%s"' % self.arg[2]
            else:
                str += "%s " % self.identifier(self.arg[4], self.arg[5])
                if self.arg[6]:
                    str += "NDATA %s" % self.arg[6]
            str += ">"
            return str

    class NotationDecl(Token):
        def __unicode__(self):
            str = self.indent_create()
            str += "<!NOTATION %s%s>" % (
                self.arg[0],
                self.identifier(self.arg[2], self.arg[3]),
            )
            return str

    class ProcessingInstruction(Token):
        def __unicode__(self):
            str = ""
            if self.preserve in [0, 1] and self.indent:
                str += self.indent_insert()
            str += "<?%s %s?>" % (self.arg[0], self.arg[1])
            return str

        def configure(self):
            super(Formatter.ProcessingInstruction, self).configure()
            self.indent = self.list.token_indent(self)

    class StartCdataSection(Token):
        def __unicode__(self):
            return "<![CDATA["

        def configure(self):
            self.list.cdata_section = True

    class StartDoctypeDecl(Token):
        def __unicode__(self):
            str = "<!DOCTYPE %s" % (self.arg[0])
            if self.arg[1]:
                str += self.identifier(self.arg[1], self.arg[2])
            if self.arg[3]:
                str += " ["
            return str

    class StartElement(Token):
        def __init__(self, list, arg):
            super(Formatter.StartElement, self).__init__(list, arg)
            self.list.level_increment()

        def __unicode__(self):
            str = ""
            if self.preserve in [0, 1] and self.indent:
                str += self.indent_insert()
            str += "<%s" % self.arg[0]
            # see issue 4: for attr in self.arg[1].keys():
            if (self.formatter.preserve_attributes):
                att_list = self.arg[1].keys()
            else:
                att_list = sorted(self.arg[1].keys())
            for attr in att_list:
                str += self.attribute(attr, self.arg[1][attr])
            if self.list[self.pos + 1].end and (self.formatter.compress or self.formatter.selfclose):
                str += "/>"
            else:
                str += ">"
            return str

        def configure(self):
            self.content_model = self.list.token_model(self)
            self.descendant_mixed = self.list.token_descendant_mixed(self)
            self.preserve = self.list.token_preserve(self)
            self.indent = self.list.token_indent(self)

    class XmlDecl(Token):
        def __init__(self, list, arg):
            super(Formatter.XmlDecl, self).__init__(list, arg)
            if len(self.arg) > 1:
                self.formatter.encoding_internal = self.arg[1]

        def __unicode__(self):
            str = "<?xml%s%s" % (
                self.attribute("version", self.arg[0]),
                self.attribute("encoding", self.formatter.encoding_effective),
            )
            if self.arg[2] > -1:
                str += self.attribute("standalone", "yes")
            str += "?>\n"
            return str


def cli_usage(msg=""):
    """ Output usage for command line tool. """
    sys.stderr.write(msg + "\n")
    sys.stderr.write(
        'Usage: xmlformat [--preserve "pre,literal"] [--blanks]\
 [--compress] [--selfclose] [--indent num] [--indent-char char]\
 [--outfile file] [--encoding enc] [--outencoding enc]\
 [--disable-inlineformatting] [--overwrite] [--disable-correction]\
 [--eof-newline] [--preserve-attributes] [--encode-attributes]\
 [--help] <--infile file | file | - >\n'
    )
    sys.exit(2)


def cli():
    """ Launch xmlformatter from command line. """
    indent = DEFAULT_INDENT
    indent_char = DEFAULT_INDENT_CHAR
    outfile = None
    overwrite = False
    preserve = []
    blanks = False
    compress = DEFAULT_COMPRESS
    selfclose = DEFAULT_SELFCLOSE
    infile = None
    encoding = DEFAULT_ENCODING_INPUT
    outencoding = DEFAULT_ENCODING_OUTPUT
    inline = DEFAULT_INLINE
    correct = DEFAULT_CORRECT
    eof_newline = DEFAULT_EOF_NEWLINE
    preserve_attributes = False
    encode_attributes = False
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "",
            [
                "compress",
                "selfclose",
                "disable-correction",
                "disable-inlineformatting",
                "encoding=",
                "help",
                "infile=",
                "indent=",
                "indent-char=",
                "outfile=",
                "outencoding=",
                "overwrite",
                "preserve=",
                "blanks",
                "eof-newline",
                "preserve-attributes",
                "encode-attributes",
            ],
        )
    except getopt.GetoptError as err:
        cli_usage(str(err))
    for key, value in opts:
        if key in ["--indent"]:
            indent = value
        elif key in ["--preserve"]:
            preserve = value.replace(",", " ").split()
        elif key in ["--blanks"]:
            blanks = True
        elif key in ["--help"]:
            cli_usage()
        elif key in ["--compress"]:
            compress = True
        elif key in ["--selfclose"]:
            selfclose = True
        elif key in ["--outfile"]:
            outfile = value
        elif key in ["--infile"]:
            infile = value
        elif key in ["--encoding"]:
            encoding = value
        elif key in ["--outencoding"]:
            outencoding = value
        elif key in ["--indent-char"]:
            indent_char = value
        elif key in ["--disable-inlineformatting"]:
            inline = False
        elif key in ["--disable-correction"]:
            correct = False
        elif key in ["--overwrite"]:
            overwrite = True
        elif key in ["--eof-newline"]:
            eof_newline = True
        elif key in ["--preserve-attributes"]:
            preserve_attributes = True
        elif key in ["--encode-attributes"]:
            encode_attributes = True
            break
    try:
        formatter = Formatter(
            indent=indent,
            preserve=preserve,
            blanks=blanks,
            compress=compress,
            selfclose=selfclose,
            encoding_input=encoding,
            encoding_output=outencoding,
            indent_char=indent_char,
            inline=inline,
            correct=correct,
            eof_newline=eof_newline,
            preserve_attributes=preserve_attributes,
            encode_attributes=encode_attributes,
        )
        if infile:
            save_formatter_result(formatter.format_file(infile), formatter, overwrite, infile, outfile)
        elif len(args) > 0:
            if args[0] == "-":
                save_formatter_result(formatter.format_string("".join(sys.stdin.readlines())), formatter, overwrite, None, outfile)
            else:
                for input_file in args:
                    save_formatter_result(formatter.format_file(input_file), formatter, overwrite, input_file, outfile)

    except xml.parsers.expat.ExpatError as err:
        cli_usage("XML error: %s" % err)
    except IOError as err:
        cli_usage("IO error: %s" % err)
    except:
        cli_usage("Unkonwn error")

def save_formatter_result(res, formatter, overwrite, input_file, outfile):
    if overwrite:
        formatter.enc_output(input_file, res)
    else:
        formatter.enc_output(outfile, res)
