#!/bin/bash

# Example: Check service health
curl -X GET https://api.toolfront.ai/health

# Example: List users with authentication
curl -X GET https://api.toolfront.ai/users \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
