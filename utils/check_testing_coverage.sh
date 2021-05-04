# Run tests to track coverage
docker exec pandas_dtype_efficiency_dev coverage run -m pytest tests/

# Produce report
docker exec pandas_dtype_efficiency_dev coverage report -m

# Produce visual report
docker exec pandas_dtype_efficiency_dev coverage html