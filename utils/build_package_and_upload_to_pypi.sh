echo "Running unit tests"
docker exec pandas_dtype_efficiency_dev pytest --verbose tests/ && \

echo "Removing build and dist directories if they already exist"
[ -d "build" ] && rm -r build
[ -d "dist" ] && rm -r dist

echo "Creating package"
docker exec pandas_dtype_efficiency_dev python setup.py sdist bdist_wheel && \

echo "Check package description will render properly on PyPI"
docker exec pandas_dtype_efficiency_dev twine check dist/* && \

echo "Uploading to PyPI"
docker exec -it pandas_dtype_efficiency_dev twine upload dist/*
