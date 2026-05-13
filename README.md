# Hybrid HA VMware + AWS

![CI](https://github.com/leopen10/hybrid-ha-vmware-aws/actions/workflows/ci.yml/badge.svg)

Infrastructure hybride haute disponibilité avec basculement automatique
entre un datacenter on-premise (VMware) et AWS.

## Problème résolu

Quand un datacenter tombe en panne, les applications doivent rester
disponibles. Ce projet implémente un mécanisme de basculement automatique
vers AWS en moins de 60 secondes, sans intervention humaine.

## Architecture

SITUATION NORMALE
─────────────────────────────────────────────
Utilisateurs → On-prem (VMware) → Applications
↑
Site principal
AWS en veille
PANNE DÉTECTÉE
─────────────────────────────────────────────
Prometheus détecte la panne
↓
Script failover se déclenche
↓
EC2 AWS démarre en 40 secondes
↓
Trafic redirigé vers AWS
RÉCUPÉRATION
─────────────────────────────────────────────
On-prem revient en ligne
↓
Script failback se déclenche
↓
EC2 AWS s'arrête
↓
Trafic redirigé vers on-prem

## Stack technique

| Composant | Technologie |
|---|---|
| Infrastructure as Code | Terraform 1.15+ |
| Cloud de secours | AWS (EC2, VPC, Security Groups) |
| Virtualisation on-prem | VMware / VirtualBox |
| Surveillance | Prometheus + Node Exporter |
| Basculement | Python 3.12 |
| CI/CD | GitHub Actions |

## Résultats prouvés

Failover  : on-prem → AWS    en 40 secondes  ✓
Failback  : AWS → on-prem    en  7 secondes  ✓
Détection : panne détectée   en  5 secondes  ✓

## Prérequis

```bash
# Terraform
terraform --version  # >= 1.0

# AWS CLI
aws --version

# Python
python3 --version  # >= 3.10

# Credentials AWS configurés
aws sts get-caller-identity
```

## Installation

```bash
git clone https://github.com/leopen10/hybrid-ha-vmware-aws.git
cd hybrid-ha-vmware-aws

# Déployer l'infrastructure AWS
cd terraform
terraform init
terraform plan
terraform apply
```

## Usage

```bash
# Tester la connexion à l'EC2
ssh -i ~/.ssh/hybrid-ha-key ubuntu@<EC2_IP>

# Déclencher un basculement manuel
python3 scripts/failover/trigger_failover.py

# Déclencher un failback manuel
python3 scripts/failover/trigger_failback.py

# Détruire l'infrastructure (économiser les coûts)
cd terraform && terraform destroy
```

## Structure

hybrid-ha-vmware-aws/
├── terraform/          # Infrastructure AWS (VPC, EC2, SG)
├── scripts/
│   ├── failover/       # Scripts failover et failback
│   └── monitoring/     # Configuration Prometheus
├── docs/               # Documentation détaillée
└── proofs/             # Logs et preuves d'exécution

## Documentation

| Document | Description |
|---|---|
| docs/architecture.md | Schéma global de l'architecture |
| docs/failover.md | Mécanisme de basculement |
| docs/networking.md | Plan réseau VPC et VLANs |
| docs/runbook.md | Runbook opérationnel |

## Auteur

**Leonel Pengou** — Cloud & DevOps Engineer
[GitHub](https://github.com/leopen10) •
[LinkedIn](https://linkedin.com/in/leonel-magloire-pengou-mba)
