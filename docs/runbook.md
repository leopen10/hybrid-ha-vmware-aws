# Runbook opérationnel — Hybrid HA

## Vérifications quotidiennes

```bash
# 1. Vérifier que Prometheus tourne sur EC2
ssh -i ~/.ssh/hybrid-ha-key ubuntu@
sudo systemctl status prometheus
sudo systemctl status node_exporter

# 2. Vérifier les métriques
curl http://localhost:9090/api/v1/targets

# 3. Vérifier la santé du site on-prem
ping -c 3 192.168.1.40
```

## Scénario 1 — Panne on-prem détectée

```bash
# Déclencher le basculement
cd ~/hybrid-ha-vmware-aws
python3 scripts/failover/trigger_failover.py

# Vérifier que EC2 tourne
aws ec2 describe-instances \
  --instance-ids i-05aac4133dd3b19e9 \
  --query 'Reservations[0].Instances[0].State.Name'

# Vérifier les logs
cat /tmp/failover.log
```

## Scénario 2 — On-prem revient en ligne

```bash
# Déclencher le failback
python3 scripts/failover/trigger_failback.py

# Vérifier que EC2 est arrêté
aws ec2 describe-instances \
  --instance-ids i-05aac4133dd3b19e9 \
  --query 'Reservations[0].Instances[0].State.Name'

# Vérifier les logs
cat /tmp/failback.log
```

## Scénario 3 — Économiser les coûts AWS

```bash
# Arrêter EC2 manuellement
aws ec2 stop-instances \
  --instance-ids i-05aac4133dd3b19e9

# Détruire toute l'infrastructure
cd terraform
terraform destroy
```

## Contacts escalade

- Responsable infra : infra@entreprise.fr
- Canal urgence : #oncall-infra (Slack)
- Astreinte : +33 X XX XX XX XX
