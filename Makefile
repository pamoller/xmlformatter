all: sdist install regress

sdist:
	rm -f MANIFEST
	python setup.py sdist
	
install:
	python setup.py install
	rm -rf /usr/lib/python2.6/site-packages/xmlformatter/

register: regress
	python setup.py register
	
regress:
	cd test && python test_xmlformatter.py

upload: regress
	#python setup.py sdist upload
	python -m twine upload dist/*
