# PoC SKU Unification

Build virtual env

python install .


https://criteo.atlassian.net/wiki/spaces/MOZART/pages/1433371141/How+to+register+a+kernel+on+JupyterLab


https://criteo.sourcegraphcloud.com/github.com/criteo/ml-hadoop-experiment/-/blob/notebooks/pytorch_offline_inference.ipynb


Upload in public PyPi:

```
python setup.py sdist
pip install twine
twine upload --repository pypi dist/*

```
