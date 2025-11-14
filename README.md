## 1️⃣ Objectif
Ce projet a pour objectif de **nettoyer et standardiser les données** clients, catalogue produits et ventes, afin de garantir leur qualité et cohérence.  
Le pipeline effectue notamment :  
- Standardisation des emails, pays et téléphones des clients  
- Conversion des dates au format ISO  
- Conversion des poids en kg et des prix en €  
- Correction des catégories produits selon un mapping officiel  
- Suppression des doublons et identification des lignes manquantes  
- Séparation des ventes valides et des remboursements  
- Calcul de KPI avant et après nettoyage

## 2️⃣ Structure des dossiers
DATACLEANSING/
│
├─ data/ 
│ ├─ clients.csv
│ ├─ catalog_fr.csv
│ ├─ catalog_us.csv
│ ├─ mapping_categories.csv
│ └─ sales.csv
│
├─ out/ # Données nettoyées
│ ├─ clients_clean.csv
│ ├─ catalog_canonique.csv
│ ├─ sales_clean.csv
│ └─ daily_revenue.csv
│
├─ reports/ # Rapports et fichiers missing
│ ├─ kpi_clients.csv
│ ├─ kpi_catalog.csv
│ ├─ kpi_sales.csv
│ ├─ clients_missing.csv
│ ├─ catalog_missing.csv
│ ├─ sales_missing.csv
│ └─ 
│  src/
├─ utils_cleaning.py # Fonctions utilitaires pour le nettoyage
└─ pipeline_cleaning.py # Script principal

## 3️⃣ Installation et prérequis

- Python 3.10+  
- Packages nécessaires : `pandas`  
```bash
#pip install pandas


5️⃣ Contenu des fichiers nettoyés
1 Clients (clients_clean.csv) 

Colonnes : id, nom, prenom, email, telephone, pays, naissance

Toutes les lignes ont des valeurs non manquantes pour les colonnes critiques

Doublons emails supprimés

2 Catalogue produits (catalog_canonique.csv)

Colonnes : sku, name, category, weight, price, currency

Poids en kg, prix en €

Catégories corrigées selon mapping_categories.csv

Doublons SKU supprimés

3 Ventes (sales_clean.csv et sales_refunds.csv)

Colonnes : order_id, customer_email, order_date, amount, currency

Dates au format ISO

Montants en €

sales_refunds.csv contient uniquement les montants négatifs

Doublons (order_id + customer_email) supprimés



6️⃣ KPI et rapports

Fichiers KPI : kpi_clients.csv, kpi_catalog.csv, kpi_sales.csv

Contiennent : nombre de lignes avant/après nettoyage, doublons supprimés, lignes manquantes, invalidités, remboursements

daily_revenue.csv : revenu journalier calculé à partir des ventes valides



7️⃣ Notes et recommandations

Les fonctions de nettoyage se trouvent dans utils_cleaning.py (emails, pays, téléphone, dates, poids, prix).

Toutes les lignes avec données critiques manquantes sont isolées dans les fichiers *_missing.csv.

Les valeurs négatives dans les ventes sont séparées dans sales_refunds.csv.



Journal de transformation des données

Ce document décrit toutes les étapes de nettoyage appliquées aux datasets clients, catalogue produits et ventes, les résultats obtenus, ainsi que les exceptions rencontrées.

1️⃣ Nettoyage des clients (clients.csv)

Objectif : standardiser les emails, les pays, les téléphones et les dates de naissance, supprimer les doublons, et isoler les lignes avec données manquantes.

Actions réalisées :

Standardisation des emails

Tous les emails ont été mis en minuscules et les espaces superflus supprimés.

Les emails invalides sont comptabilisés dans les KPI mais conservés dans clients_clean.csv.

Standardisation des pays

Les noms des pays ont été uniformisés (ex. "France").

Les valeurs manquantes sont isolées dans clients_missing.csv.

Standardisation des téléphones

Formatage international appliqué, suppression des caractères invalides.

Les lignes avec téléphones manquants ou incorrects sont déplacées vers clients_missing.csv.

Standardisation des dates de naissance

Conversion en format ISO (YYYY-MM-DD).

Les dates manquantes sont isolées dans clients_missing.csv.

Suppression des doublons

Les doublons sur la colonne email ont été supprimés.

Résultat :

50 000 lignes d’origine → 47 498 lignes nettoyées, 2 502 lignes isolées dans clients_missing.csv.

KPI détaillés générés dans kpi_clients.csv.

2️⃣ Nettoyage du catalogue produits (catalog_fr.csv et catalog_us.csv)

Objectif : unifier les unités de poids, les prix en €, corriger les catégories et supprimer les doublons.

Actions réalisées :

Conversion des poids en kg

Les poids exprimés en grammes ou livres ont été convertis en kilogrammes.

Les lignes sans poids valide sont isolées dans catalog_missing.csv.

Conversion des prix en €

Tous les prix sont maintenant directement en euros.

Les lignes sans prix valide sont isolées dans catalog_missing.csv.

Correction des catégories

Les catégories des produits ont été mappées selon le fichier mapping_categories.csv.

Les lignes dont la catégorie ne peut être mappée sont isolées dans catalog_missing.csv.

Suppression des doublons SKU

Chaque produit est identifié de manière unique par son SKU.

Résultat :

Catalogue fusionné : catalog_canonique.csv contient toutes les lignes valides.

Les lignes avec valeurs critiques manquantes sont stockées dans catalog_missing.csv.

3️⃣ Nettoyage des ventes (sales.csv)

Objectif : mettre les dates au format ISO, vérifier les montants positifs, séparer les remboursements, supprimer les doublons et isoler les lignes avec données manquantes.

Actions réalisées :

Standardisation des dates

Conversion en format ISO (YYYY-MM-DD).

Les dates manquantes sont isolées dans sales_missing.csv.

Standardisation des emails clients

Minuscules, suppression des espaces.

Les emails manquants sont isolés dans sales_missing.csv.

Conversion des montants en €

Les montants en USD ont été convertis en euros.

Les montants invalides sont isolés dans sales_missing.csv.

Séparation des remboursements

Les ventes avec montants négatifs sont extraites dans sales_refunds.csv et retirées de sales_clean.csv.

Suppression des doublons

Les doublons identifiés par order_id + customer_email sont supprimés.

Résultat :

sales_clean.csv contient uniquement les ventes valides.

sales_missing.csv contient les lignes avec données critiques manquantes.

sales_refunds.csv contient tous les remboursements.

KPI détaillés disponibles dans kpi_sales.csv.



Pour ce qui est de kpi voila :
Clients (kpi_clients.csv)

Nombre de lignes avant et après nettoyage.

Nombre de doublons supprimés.

Pourcentage d’emails invalides.

Nombre de lignes avec informations manquantes.

Catalogue produits (kpi_catalog.csv)

Nombre de lignes avant et après nettoyage.

Nombre de doublons SKU supprimés.

Nombre de lignes avec poids, prix ou catégorie manquante.

Ventes (kpi_sales.csv)

Nombre de lignes avant et après nettoyage.

Nombre de doublons supprimés.

Nombre de lignes avec dates ou montants invalides.

Nombre de remboursements extraits.



on a aussi rajouter une visualisation graphique des kpi , pour y avoir accees il faut faire 
 pip install matplotlib.pyplot  puis import matplotlib.pyplot as plt



 PS: il ya une fonction qu'ona ajouter directement car ca ne voulais pas marcher quand on la mettait sur utils_cleaning 


 AUTEURS : BENBAHAZ Hakem amine
           BELLIL Samy