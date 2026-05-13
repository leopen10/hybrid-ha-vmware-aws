#!/usr/bin/env python3
"""
trigger_failback.py — Retour vers le site on-prem après récupération
"""

import json
import sys
import subprocess
from datetime import datetime


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("/tmp/failback.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def check_onprem_health(onprem_ip):
    """Vérifie si le site on-prem est revenu."""
    result = subprocess.run(
        ["ping", "-c", "5", "-W", "2", onprem_ip],
        capture_output=True
    )
    return result.returncode == 0


def stop_ec2_instance(instance_id, region):
    """Arrête l'instance EC2 de secours."""
    log(f"Arrêt de l'instance EC2 {instance_id}...")
    result = subprocess.run([
        "aws", "ec2", "stop-instances",
        "--instance-ids", instance_id,
        "--region", region
    ], capture_output=True, text=True)

    if result.returncode == 0:
        log(f"Instance {instance_id} arrêtée")
        return True
    else:
        log(f"Erreur arrêt EC2 : {result.stderr}")
        return False


def update_cmdb(status, reason):
    """Enregistre le failback dans la CMDB."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "FAILBACK",
        "status": status,
        "active_site": "ON-PREM",
        "reason": reason
    }
    with open("/tmp/cmdb_failover.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    log(f"CMDB mise à jour : {status}")


def main():
    ONPREM_IP    = "192.168.1.40"
    EC2_INSTANCE = "i-05aac4133dd3b19e9"
    AWS_REGION   = "us-east-1"

    log("=" * 50)
    log("DÉCLENCHEMENT DU FAILBACK VERS ON-PREM")
    log("=" * 50)

    # Étape 1 — Vérifier que on-prem est revenu
    log("Vérification de la santé du site on-prem...")
    if not check_onprem_health(ONPREM_IP):
        log("ERREUR : on-prem toujours inaccessible — failback annulé")
        sys.exit(1)

    log("Confirmé : site on-prem accessible")

    # Étape 2 — Arrêter l'instance EC2
    if not stop_ec2_instance(EC2_INSTANCE, AWS_REGION):
        log("ERREUR : impossible d'arrêter l'instance EC2")
        sys.exit(1)

    # Étape 3 — Mettre à jour la CMDB
    update_cmdb("SUCCESS", "on-prem recovered")

    log("=" * 50)
    log("FAILBACK TERMINÉ")
    log("Trafic redirigé vers ON-PREM : " + ONPREM_IP)
    log("Instance EC2 arrêtée pour économiser les coûts")
    log("=" * 50)


if __name__ == "__main__":
    main()
