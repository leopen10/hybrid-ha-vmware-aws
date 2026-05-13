# Architecture — Hybrid HA VMware + AWS

## Vue d'ensemble

┌─────────────────────────────────────────────────────────────┐
│                    SITE ON-PREM (VMware)                    │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   VM Web     │    │   VM App     │    │  Prometheus  │  │
│  │ 192.168.1.40 │    │ 192.168.1.41 │    │ 192.168.1.42 │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                              │                              │
└──────────────────────────────┼──────────────────────────────┘
│ VPN site-à-site
│ (IPsec + BGP)
┌──────────────────────────────┼──────────────────────────────┐
│                    SITE AWS (us-east-1)                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  VPC 10.0.0.0/16                                    │   │
│  │                                                     │   │
│  │  ┌──────────────────┐  ┌──────────────────────┐    │   │
│  │  │  Subnet Public   │  │   Subnet Privé       │    │   │
│  │  │  10.0.1.0/24     │  │   10.0.2.0/24        │    │   │
│  │  │                  │  │                      │    │   │
│  │  │  ┌────────────┐  │  │                      │    │   │
│  │  │  │ EC2 Standby│  │  │                      │    │   │
│  │  │  │ t3.micro   │  │  │                      │    │   │
│  │  │  └────────────┘  │  │                      │    │   │
│  │  └──────────────────┘  └──────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

## Composants

### On-prem
- **VMware ESXi** — hyperviseur qui fait tourner les VMs
- **VMs Linux** — serveurs applicatifs
- **Prometheus** — surveille la santé de toutes les VMs

### AWS
- **VPC** — réseau privé isolé sur AWS
- **Subnet public** — accessible depuis internet
- **Subnet privé** — isolé, pour les données sensibles
- **EC2 t3.micro** — instance de secours en veille
- **Security Group** — pare-feu qui contrôle les accès
- **Internet Gateway** — porte vers internet

### Scripts
- **trigger_failover.py** — bascule vers AWS quand on-prem tombe
- **trigger_failback.py** — revient vers on-prem quand il récupère

## Flux de trafic

### Mode normal

Utilisateur → DNS → On-prem IP → VMs VMware

### Mode basculement
Prometheus détecte panne
→ trigger_failover.py
→ EC2 démarre
→ Trafic redirigé vers EC2 IP

### Mode failback
Prometheus détecte récupération
→ trigger_failback.py
→ EC2 s'arrête
→ Trafic revient vers on-prem
