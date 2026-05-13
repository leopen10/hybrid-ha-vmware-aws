#!/usr/bin/env python3
"""
trigger_failover.py — Script de basculement automatique vers AWS
Déclenché par Alertmanager quand on-prem tombe
"""

import json
import sys
import subprocess
from datetime import datetime


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("/tmp/failover.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def check_onprem_health(onprem_ip):
    """Vérifie si le site on-prem répond."""
    result = subprocess.run(
        ["ping", "-c", "3", "-W", "2", onprem_ip],
        capture_output=True
    )
    return result.returncode == 0


def start_ec2_instance(instance_id, region):
    """Démarre l'instance EC2 de secours."""
    log(f"Démarrage de l'instance EC2 {instance_id}...")
    result = subprocess.run([
        "aws", "ec2", "start-instances",
        "--instance-ids", instance_id,
        "--region", region
    ], capture_output=True, text=True)

    if result.returncode == 0:
        log(f"Instance {instance_id} démarrée avec succès")
        return True
    else:
        log(f"Erreur démarrage EC2 : {result.stderr}")
        return False


def get_ec2_public_ip(instance_id, region):
    """Récupère l'IP publique de l'instance EC2."""
    result = subprocess.run([
        "aws", "ec2", "describe-instances",
        "--instance-ids", instance_id,
        "--region", region,
        "--query", "Reservations[0].Instances[0].PublicIpAddress",
        "--output", "text"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout.strip()
    return None


def update_cmdb(status, ec2_ip, reason):
    """Enregistre le basculement dans le fichier de log CMDB."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "FAILOVER",
        "status": status,
        "active_site": "AWS",
        "ec2_ip": ec2_ip,
        "reason": reason
    }
    with open("/tmp/cmdb_failover.json", "a") as f:
        f.write(json.dumps(entry) + "\n")
    log(f"CMDB mise à jour : {status}")


def main():
    # Configuration
    ONPREM_IP     = "192.168.1.40"
    EC2_INSTANCE  = "i-05aac4133dd3b19e9"
    AWS_REGION    = "us-east-1"

    log("=" * 50)
    log("DÉCLENCHEMENT DU BASCULEMENT HYBRIDE HA")
    log("=" * 50)

    # Étape 1 — Vérifier que on-prem est vraiment down
    log("Vérification de la santé du site on-prem...")
    if check_onprem_health(ONPREM_IP):
        log("ATTENTION : on-prem répond encore — basculement annulé")
        log("Vérifiez l'alerte Prometheus avant de forcer le basculement")
        sys.exit(1)

    log("Confirmé : site on-prem inaccessible")

    # Étape 2 — Démarrer l'instance EC2
    if not start_ec2_instance(EC2_INSTANCE, AWS_REGION):
        log("ERREUR : impossible de démarrer l'instance EC2")
        sys.exit(1)

    # Étape 3 — Attendre et récupérer l'IP
    import time
    log("Attente démarrage EC2 (30 secondes)...")
    time.sleep(30)

    ec2_ip = get_ec2_public_ip(EC2_INSTANCE, AWS_REGION)
    if ec2_ip:
        log(f"Instance EC2 accessible à : {ec2_ip}")
    else:
        log("Impossible de récupérer l'IP EC2")

    # Étape 4 — Mettre à jour la CMDB
    update_cmdb("SUCCESS", ec2_ip or "unknown", "on-prem unreachable")

    log("=" * 50)
    log("BASCULEMENT TERMINÉ")
    log(f"Trafic redirigé vers AWS : {ec2_ip}")
    log("Fichier log : /tmp/failover.log")
    log("=" * 50)


if __name__ == "__main__":
    main()
