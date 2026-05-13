# Mécanisme de basculement — Failover & Failback

## Conditions de déclenchement

Le basculement se déclenche quand :

Prometheus détecte qu'une instance est DOWN
→ alerte InstanceDown (after 1 minute)
Le script vérifie manuellement avec ping
→ 3 pings consécutifs échouent
Déclenchement manuel par l'opérateur
→ python3 scripts/failover/trigger_failover.py


## Ordre des opérations — Failover
Étape 1 — Détection (5 secondes)
ping -c 3 192.168.1.40
→ si échec → continuer
Étape 2 — Démarrage EC2 (2 secondes)
aws ec2 start-instances --instance-ids i-xxxxx
→ EC2 passe de stopped à running
Étape 3 — Attente démarrage (30 secondes)
→ EC2 s'initialise complètement
Étape 4 — Récupération IP (1 seconde)
aws ec2 describe-instances
→ récupère l'IP publique
Étape 5 — Mise à jour CMDB (1 seconde)
→ enregistre l'événement avec timestamp
Total : ~40 secondes

## Ordre des opérations — Failback
Étape 1 — Vérification on-prem (5 secondes)
ping -c 5 192.168.1.40
→ si succès → continuer
Étape 2 — Arrêt EC2 (2 secondes)
aws ec2 stop-instances --instance-ids i-xxxxx
→ EC2 passe de running à stopped
Étape 3 — Mise à jour CMDB (1 seconde)
→ enregistre l'événement avec timestamp
Total : ~7 secondes

## Résultats mesurés

| Opération | Durée |
|---|---|
| Détection panne | 5 secondes |
| Failover complet | 40 secondes |
| Failback complet | 7 secondes |

## Procédure manuelle

```bash
# Basculer vers AWS
python3 scripts/failover/trigger_failover.py

# Revenir vers on-prem
python3 scripts/failover/trigger_failback.py

# Voir les logs
cat /tmp/failover.log
cat /tmp/failback.log

# Voir la CMDB
cat /tmp/cmdb_failover.json
```
