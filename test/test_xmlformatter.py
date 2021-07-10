import io
import os
import unittest
import xmlformatter
import shutil

class TestXmlFormatter(unittest.TestCase):
	
	def readfile(self, path):
		fh = io.open(path, "rb")
		text = fh.read()
		fh.close()
		return text

	def test_pretty(self):
		self.formatter = xmlformatter.Formatter()
		self.assertEqual(self.formatter.format_file("t1.xml"), self.readfile("t1_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t2.xml"), self.readfile("t2_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t4.xml"), self.readfile("t4_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t5.xml"), self.readfile("t5_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t7.xml"), self.readfile("t7_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t8.xml"), self.readfile("t8_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t9.xml"), self.readfile("t9_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t10.xml"), self.readfile("t10_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t11.xml"), self.readfile("t11_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t12.xml"), self.readfile("t12_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t13.xml"), self.readfile("t13_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t14.xml"), self.readfile("t14_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t15.xml"), self.readfile("t15_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t16.xml"), self.readfile("t16_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t17.xml"), self.readfile("t17_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t20.xml"), self.readfile("t20_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t21.xml"), self.readfile("t21_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t25.xml"), self.readfile("t25_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t24.xml"), self.readfile("t24.xml"))
		self.assertEqual(self.formatter.format_file("t26.xml"), self.readfile("t26.xml"))
		self.assertEqual(self.formatter.format_file("t27.xml"), self.readfile("t27.xml"))
		self.assertEqual(self.formatter.format_file("t28.xml"), self.readfile("t28_pretty.xml"))
		self.assertEqual(self.formatter.format_file("t31.xml"), self.readfile("t31_pretty.xml"))

	def test_disable_inline_formatting(self):
		self.formatter = xmlformatter.Formatter(inline=False)
		self.assertEqual(self.formatter.format_file("t29.xml"), self.readfile("t29_pretty.xml"))

	def test_pretty_precede(self):
		self.formatter = xmlformatter.Formatter(preserve=["precede"])
		self.assertEqual(self.formatter.format_file("t6.xml"), self.readfile("t6_pretty.xml"))
		self.formatter.preserve = ['root']
		self.assertEqual(self.formatter.format_file("t21.xml"), self.readfile("t21_precede.xml"))

	def test_encoding(self):
		self.formatter = xmlformatter.Formatter(encoding_output="UTF-8")
		# Different output encoding:
		self.assertEqual(self.formatter.format_file("t18.xml"), self.readfile("t18_utf-8.xml"))
		self.formatter = xmlformatter.Formatter(encoding_input="ISO-8859-1")
		# Set right input encoding and output it
		self.assertEqual(self.formatter.format_file("t19.xml"), self.readfile("t19.xml"))
		# Umls erverywhere
		self.assertEqual(self.formatter.format_file("t30.xml"), self.readfile("t30.xml"))

	def test_indent_char(self):
		self.formatter = xmlformatter.Formatter(indent_char="\t", indent="2")
		self.assertEqual(self.formatter.format_file("t22.xml"), self.readfile("t22_pretty.xml"))

	def test_compress(self):
		self.formatter = xmlformatter.Formatter(compress=True)
		self.assertEqual(self.formatter.format_file("t2.xml"), self.readfile("t2_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t4.xml"), self.readfile("t4_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t7.xml"), self.readfile("t7_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t8.xml"), self.readfile("t8_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t9.xml"), self.readfile("t9_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t10.xml"), self.readfile("t10_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t12.xml"), self.readfile("t12_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t13.xml"), self.readfile("t13_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t14.xml"), self.readfile("t14_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t15.xml"), self.readfile("t15_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t16.xml"), self.readfile("t16_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t17.xml"), self.readfile("t17_compressed.xml"))
		self.assertEqual(self.formatter.format_file("t20.xml"), self.readfile("t20_compressed.xml"))
		#self.assertEqual(self.formatter.format_file("t32.xml"), self.readfile("t32.xml"))

	def test_compressed_precede(self):
		self.formatter = xmlformatter.Formatter(preserve=["precede"], compress=True)
		self.assertEqual(self.formatter.format_file("t6.xml"), self.readfile("t6_compressed.xml"))

	def test_disable_correction(self):
		self.formatter = xmlformatter.Formatter(correct = False)
		self.assertEqual(self.formatter.format_file("t1.xml"), self.readfile("t1.xml"))

	def test_overwrite(self):
		shutil.copyfile("t1.xml", "t1_copy.xml")
		os.system("xmlformat --overwrite t1_copy.xml")
		self.assertEqual(self.readfile("t1_copy.xml"), self.readfile("t1_pretty.xml"))

	def test_newline_at_eof(self):
		self.formatter = xmlformatter.Formatter(eof_newline=True)
		self.assertEqual(self.formatter.format_file("t28.xml"), self.readfile("t28_pretty_with_eof_newline.xml"))
	

	#TODO cmd testing
	#def test_file_options(self):
	#	os.system("xmlformat --infile t1.xml --outfile t1_out.xml");
	#	#self.assertEqual(self.readfile("t1.xml"), self.readfile("t1_out.xml"));
	#	self.assertTrue(True)


if __name__ == '__main__':
	unittest.main()
