#!/bin/bash
# boilerplate.sh: Convert sample files to project–specific files by replacing placeholders.
# Usage: ./boilerplate.sh <api-name>

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <api-name>"
  exit 1
fi

API_NAME="$1"
echo "Starting boilerplate conversion for API: ${API_NAME}..."

# Remove sample files.
echo "Removing sample endpoints and test files..."
rm -rf ../src/api/v1/endpoints/hello.py ../src/services/hello_service.py \
       ../tests/unit/test_hello.py ../tests/integration/test_db.py

# Update README.md
if [ -f ../README.md ]; then
  echo "Updating README.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" ../README.md
else
  echo "README.md not found. Creating README.md with seed content..."
  cat <<EOF > ../README.md
# ${API_NAME}

Welcome to the ${API_NAME} API.
This project is now set up and ready for development.
EOF
fi

# Update documentation files.
if [ -f ../docs/api/endpoints.md ]; then
  echo "Updating docs/api/endpoints.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" ../docs/api/endpoints.md
else
  echo "File docs/api/endpoints.md not found. Skipping..."
fi

if [ -f ../docs/evolution_guide.md ]; then
  echo "Updating docs/evolution_guide.md with API name..."
  sed -i "s/{{api-name}}/${API_NAME}/g" ../docs/evolution_guide.md
else
  echo "File docs/evolution_guide.md not found. Skipping..."
fi

# Update Docker Compose files.
for file in ../devops/docker-compose.yml ../devops/docker-compose.test.yml; do
  if [ -f "$file" ]; then
    echo "Updating $file with API name for POSTGRES_DB..."
    sed -i "s/{{api-name}}/${API_NAME}/g" "$file"
  else
    echo "File $file not found. Skipping..."
  fi
done

# Update .devcontainer/devcontainer.json if it exists.
if [ -f ../.devcontainer/devcontainer.json ]; then
  echo "Updating .devcontainer/devcontainer.json with API name..."
  sed -i "s/{{ api-name }}/${API_NAME}/g" ../.devcontainer/devcontainer.json
else
  echo ".devcontainer/devcontainer.json not found. Skipping..."
fi

# Remove existing git history and reinitialize repository.
if [ -d ../.git ]; then
  echo "Removing existing .git directory..."
  rm -rf ../.git
fi

echo "Initializing new git repository..."
cd .. && git init
git add .
git commit -m "Initial commit - boilerplate conversion for ${API_NAME}"

echo "Boilerplate conversion complete. Your repository is now set up with API name: ${API_NAME}"
