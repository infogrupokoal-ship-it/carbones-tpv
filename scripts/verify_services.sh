#!/bin/bash
# Test Script to simulate/verify services boot and UFW configuration

echo "=== Verifying Enterprise Services ==="
for service in tpv tpv-sync tpv-hardware tpv-maintenance.timer; do
    systemctl is-active --quiet $service && echo "✅ $service is RUNNING" || echo "❌ $service is DOWN or not loaded"
done

echo ""
echo "=== Verifying UFW Status ==="
sudo ufw status verbose

echo ""
echo "=== Verifying Nginx ==="
sudo nginx -t

echo ""
echo "✅ Verification complete."
