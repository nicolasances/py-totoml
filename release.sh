python3 setup.py sdist bdist_wheel;
python3 -m twine upload dist/*;
rm -rf dist;
rm -rf totoml.egg-info;
rm -rf build;
rm -rf __pycache__;