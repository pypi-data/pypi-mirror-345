<p>Lire la <a href="https://10.0.2.25/docs/Librairie%20Python/lial_user_bdd/">Documentation</a></p>

python setup.py sdist bdist_wheel

twine upload --config-file .venv/.pypirc ./dist/*