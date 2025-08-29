#!/bin/bash

# fruxAI Kong Gateway Setup Script
# This script configures Kong Gateway routes for fruxAI services

set -e

KONG_ADMIN_URL=${KONG_ADMIN_URL:-"http://localhost:8001"}
FRUXAI_API_URL=${FRUXAI_API_URL:-"http://fruxai-api:8001"}
N8N_URL=${N8N_URL:-"http://n8n:5678"}

echo "Setting up Kong Gateway routes for fruxAI..."

# Function to make Kong API calls
kong_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ "$method" = "GET" ]; then
        curl -s -X $method "$KONG_ADMIN_URL$endpoint"
    else
        curl -s -X $method "$KONG_ADMIN_URL$endpoint" \
             -H "Content-Type: application/json" \
             -d "$data"
    fi
}

# Wait for Kong to be ready
echo "Waiting for Kong Gateway..."
until curl -s "$KONG_ADMIN_URL/status" > /dev/null; do
    echo "Kong not ready, waiting..."
    sleep 5
done

echo "Kong Gateway is ready!"

# 1. Create fruxAI API service
echo "Creating fruxAI API service..."
SERVICE_RESPONSE=$(kong_call POST "/services" "{
    \"name\": \"fruxai-api\",
    \"url\": \"$FRUXAI_API_URL\"
}")

if echo "$SERVICE_RESPONSE" | grep -q "created_at"; then
    echo "✅ fruxAI API service created successfully"
else
    echo "❌ Failed to create fruxAI API service: $SERVICE_RESPONSE"
    exit 1
fi

# 2. Create fruxAI API route
echo "Creating fruxAI API route..."
ROUTE_RESPONSE=$(kong_call POST "/routes" "{
    \"service\": { \"name\": \"fruxai-api\" },
    \"paths\": [\"/fruxAI/api/v1\"],
    \"strip_path\": false,
    \"preserve_host\": false
}")

if echo "$ROUTE_RESPONSE" | grep -q "created_at"; then
    echo "✅ fruxAI API route created successfully"
else
    echo "❌ Failed to create fruxAI API route: $ROUTE_RESPONSE"
    exit 1
fi

# 3. Create n8n service
echo "Creating n8n service..."
N8N_SERVICE_RESPONSE=$(kong_call POST "/services" "{
    \"name\": \"n8n\",
    \"url\": \"$N8N_URL\"
}")

if echo "$N8N_SERVICE_RESPONSE" | grep -q "created_at"; then
    echo "✅ n8n service created successfully"
else
    echo "❌ Failed to create n8n service: $N8N_SERVICE_RESPONSE"
    exit 1
fi

# 4. Create n8n route
echo "Creating n8n route..."
N8N_ROUTE_RESPONSE=$(kong_call POST "/routes" "{
    \"service\": { \"name\": \"n8n\" },
    \"paths\": [\"/n8n\"],
    \"strip_path\": false,
    \"preserve_host\": false
}")

if echo "$N8N_ROUTE_RESPONSE" | grep -q "created_at"; then
    echo "✅ n8n route created successfully"
else
    echo "❌ Failed to create n8n route: $N8N_ROUTE_RESPONSE"
    exit 1
fi

# 5. Add rate limiting plugin to fruxAI API
echo "Adding rate limiting plugin..."
RATE_LIMIT_RESPONSE=$(kong_call POST "/plugins" "{
    \"name\": \"rate-limiting\",
    \"service\": { \"name\": \"fruxai-api\" },
    \"config\": {
        \"minute\": 60,
        \"hour\": 1000,
        \"day\": 5000,
        \"limit_by\": \"ip\",
        \"policy\": \"local\"
    }
}")

if echo "$RATE_LIMIT_RESPONSE" | grep -q "created_at"; then
    echo "✅ Rate limiting plugin added successfully"
else
    echo "❌ Failed to add rate limiting plugin: $RATE_LIMIT_RESPONSE"
fi

# 6. Add CORS plugin
echo "Adding CORS plugin..."
CORS_RESPONSE=$(kong_call POST "/plugins" "{
    \"name\": \"cors\",
    \"service\": { \"name\": \"fruxai-api\" },
    \"config\": {
        \"origins\": [\"*\"],
        \"methods\": [\"GET\", \"POST\", \"PUT\", \"DELETE\", \"OPTIONS\"],
        \"headers\": [\"Accept\", \"Accept-Version\", \"Content-Length\", \"Content-MD5\", \"Content-Type\", \"Date\", \"X-Auth-Token\"],
        \"exposed_headers\": [\"X-Auth-Token\"],
        \"credentials\": true,
        \"max_age\": 3600
    }
}")

if echo "$CORS_RESPONSE" | grep -q "created_at"; then
    echo "✅ CORS plugin added successfully"
else
    echo "❌ Failed to add CORS plugin: $CORS_RESPONSE"
fi

# 7. Add request transformer for fruxAI API
echo "Adding request transformer plugin..."
TRANSFORMER_RESPONSE=$(kong_call POST "/plugins" "{
    \"name\": \"request-transformer\",
    \"service\": { \"name\": \"fruxai-api\" },
    \"config\": {
        \"add\": {
            \"headers\": [\"X-fruxAI-Request: true\"]
        }
    }
}")

if echo "$TRANSFORMER_RESPONSE" | grep -q "created_at"; then
    echo "✅ Request transformer plugin added successfully"
else
    echo "❌ Failed to add request transformer plugin: $TRANSFORMER_RESPONSE"
fi

# 8. Verify configuration
echo ""
echo "Verifying Kong configuration..."
echo "Services:"
SERVICES=$(kong_call GET "/services")
echo "$SERVICES" | jq '.data[] | {name: .name, url: .url}' 2>/dev/null || echo "$SERVICES"

echo ""
echo "Routes:"
ROUTES=$(kong_call GET "/routes")
echo "$ROUTES" | jq '.data[] | {service: .service.name, paths: .paths}' 2>/dev/null || echo "$ROUTES"

echo ""
echo "✅ Kong Gateway setup completed successfully!"
echo ""
echo "fruxAI endpoints:"
echo "  - API: http://localhost:8000/fruxAI/api/v1/"
echo "  - n8n: http://localhost:8000/n8n/"
echo ""
echo "Direct access (for development):"
echo "  - API: http://localhost:8001/"
echo "  - n8n: http://localhost:5678/"
