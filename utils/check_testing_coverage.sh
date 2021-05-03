# Run tests to track coverage
docker exec pandas_dtype_efficiency_dev /home/docker_user/.local/bin/coverage run -m pytest tests/

# Produce report
docker exec pandas_dtype_efficiency_dev /home/docker_user/.local/bin/coverage report -m

# Produce visual report
docker exec pandas_dtype_efficiency_dev /home/docker_user/.local/bin/coverage html