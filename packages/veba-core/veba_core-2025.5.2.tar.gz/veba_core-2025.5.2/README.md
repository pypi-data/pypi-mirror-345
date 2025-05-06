# VEBA Core
Core utility functions and objects for VEBA

## Install
```
pip install veba-core
```

## Create SQLite database from VEBA essentials

From the CLI
```bash
output_database="./test/test-no-sequences.db" # sqlite:/// is preprended internally
veba_essentials_directory="./test/veba_output/essentials"
build-relational-database.py -i ${veba_essentials_directory} -o ${output_database}
```

From the API
```python
database_url =  "sqlite:///./test/test-no-sequences.db" 
veba_essentials_directory = "./test/veba_output/essentials"
store_sequences = False

db_controller = VEBAEssentialsDatabase(
    database_url=database_url,
    veba_essentials_directory=veba_essentials_directory,
    store_sequences=store_sequences
)
db_controller.populate_all(reset_first=True)

# --- Starting Full Database Population ---
# Loading and preparing source data...
# Parsing protein annotations structure...
# Parsing protein annotations: 100%|██████████| 139448/139448 [00:54<00:00, 2573.73 proteins/s]
# Skipping protein sequence loading (store_sequences=False).

# --- Stage 1: Samples, Pangenomes, Orthologs, HMM Lookups ---
# Populating samples...
# Adding samples: 100%|██████████| 4/4 [00:00<00:00, 151.80 samples/s]
# Samples populated (Added: 4, Skipped Existing: 0).
# Populating pangenomes...
# Found 32 unique pangenome IDs.
# Adding Pangenomes: 100%|██████████| 32/32 [00:00<00:00, 899.75 pangenomes/s]
# Pangenomes populated (Added: 32, Skipped Existing: 0).
# Flushed Samples and Pangenomes...
# Populating orthologs...
# Adding Orthologs: 100%|██████████| 122912/122912 [01:42<00:00, 1196.05 orthologs/s]
# Orthologs populated (Added: 122912 [Linked: 122912, Unlinked/Skipped: 0], Skipped Existing: 0).
# Populating HMM lookup tables...
# Ensuring HMM objects: 100%|██████████| 5/5 [00:00<00:00, 19.18 HMM DBs/s]
# HMM objects ensured (Added: 14882, Found Existing: 0).
# Attempting to commit Stage 1: Samples, Pangenomes, Orthologs, HMM Lookups...
# Commit successful for Stage 1: Samples, Pangenomes, Orthologs, HMM Lookups.
# --- Stage 1: Samples, Pangenomes, Orthologs, HMM Lookups Complete ---

# --- Stage 2: Genomes ---
# Populating genomes...
# Adding genomes: 100%|██████████| 43/43 [00:00<00:00, 1572.96 genomes/s]
# Genomes populated (Added: 43, Skipped Existing: 0, Link Errors: 0).
# Attempting to commit Stage 2: Genomes...
# Commit successful for Stage 2: Genomes.
# --- Stage 2: Genomes Complete ---

# --- Stage 2.5: Update Genome Paths ---
# Updating genome sequence file paths...

# Updating AA paths: 100%|██████████| 43/43 [00:00<00:00, 2097.13 files/s]
# Updating CDS paths: 100%|██████████| 43/43 [00:00<00:00, 2243.03 files/s]
# Genome paths updated (AA: 43, CDS: 43, Genomes Not Found: 0).
# Attempting to commit Stage 2.5: Update Genome Paths...
# Commit successful for Stage 2.5: Update Genome Paths.
# --- Stage 2.5: Update Genome Paths Complete ---

# --- Stage 3: Contigs ---
# Populating contigs...
# Adding contigs: 100%|██████████| 43/43 [00:56<00:00,  1.31s/ genomes]
# Contigs populated (Added: 29759, Skipped Existing: 0, Genome Not Found Errors: 0).
# Attempting to commit Stage 3: Contigs...
# Commit successful for Stage 3: Contigs.
# --- Stage 3: Contigs Complete ---

# --- Stage 4: Proteins & M2M Links ---
# Populating proteins and linking annotations...
# Cached 7473 objects for Pfam
# Cached 4 objects for NCBIfamAMR
# Cached 5399 objects for KOfam
# Cached 1960 objects for Enzyme
# Cached 46 objects for AntiFam
# Adding proteins: 100%|██████████| 139448/139448 [01:17<00:00, 1804.67 proteins/s]
# Proteins populated (Added: 139448, Skipped Existing: 0, Link Errors: 0).
# Attempting to commit Stage 4: Proteins & M2M Links...
# Commit successful for Stage 4: Proteins & M2M Links.
# --- Stage 4: Proteins & M2M Links Complete ---

# --- Database Population Finished Successfully ---
# --- Database Object Summary ---
# Available tables for summary: ['antifam', 'contig', 'enzyme', 'genome', 'kofam', 'ncbifam_amr', 'ortholog', 'pangenome', 'pfam', 'protein', 'protein_antifam_association', 'protein_enzyme_association', 'protein_kofam_association', 'protein_ncbifam_amr_association', 'protein_pfam_association', 'sample']
# - sample: 4
# - pangenome: 32
# - genome: 43
# - ortholog: 122912
# - contig: 29759
# - protein: 139448
# - pfam: 7473
# - kofam: 5399
# - ncbifam_amr: 4
# - antifam: 46
# - enzyme: 1960
# -----------------------------
# CPU times: user 4min 19s, sys: 11.3 s, total: 4min 30s
# Wall time: 10min 11s

```

## Converting SQLite to PostgreSQL
### Install `pgloader`
```
sudo apt install postgresql postgresql-contrib pgloader
```
### Start PostgreSQL server
```
sudo systemctl start postgresql
# sudo systemctl enable postgresql # To start on boot
sudo systemctl status postgresql
```

### Set up user
```
# Create a user
sudo -u postgres psql -c "CREATE USER veba WITH PASSWORD 'hello-postgresql';"

# Remove a user
# sudo -u postgres psql -c "DROP USER veba;"

# Check user
sudo -u postgres psql -c "\du"

                                   List of roles
 Role name |                         Attributes                         | Member of 
-----------+------------------------------------------------------------+-----------
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
 veba      |                                                            | {}

```

### Create PostgreSQL database
```
postgresql_database_name="veba-essentials-database"
sudo -u postgres psql -c "CREATE DATABASE \"${postgresql_database_name}\";"
```



### Convert to PostgreSQL
```
export PGUSER="veba"
export PGPASSWORD="hello-postgresql"
export PGHOST="localhost"
export PGPORT=5432

pgloader test-case-study.db postgresql://${PGUSER}:${PGPASSWORD}@${PGHOST}:${PGPORT}/${postgresql_database_name}
```

### Connect to PostgreSQL database
#### Connect

```
psql -U ${PGUSER} -d ${postgresql_database_name}
```

#### List all tables
```
\dt
                    List of relations
 Schema |              Name               | Type  | Owner 
--------+---------------------------------+-------+-------
 public | antifam                         | table | veba
 public | contig                          | table | veba
 public | enzyme                          | table | veba
 public | genome                          | table | veba
 public | kofam                           | table | veba
 public | ncbifam_amr                     | table | veba
 public | ortholog                        | table | veba
 public | pangenome                       | table | veba
 public | pfam                            | table | veba
 public | protein                         | table | veba
 public | protein_antifam_association     | table | veba
 public | protein_enzyme_association      | table | veba
 public | protein_kofam_association       | table | veba
 public | protein_ncbifam_amr_association | table | veba
 public | protein_pfam_association        | table | veba
 public | sample                          | table | veba
(16 rows)
```


#### Describe a table
```
\d protein
                Table "public.protein"
   Column    |  Type  | Collation | Nullable | Default 
-------------+--------+-----------+----------+---------
 name        | text   |           | not null | 
 cds         | text   |           |          | 
 aa          | text   |           |          | 
 md5_cds     | text   |           |          | 
 md5_aa      | text   |           |          | 
 length      | bigint |           |          | 
 product     | text   |           |          | 
 uniref      | text   |           |          | 
 mibig       | text   |           |          | 
 vfdb        | text   |           |          | 
 cazy        | text   |           |          | 
 contig_id   | text   |           |          | 
 ortholog_id | text   |           |          | 
Indexes:
    "idx_16437_sqlite_autoindex_protein_1" PRIMARY KEY, btree (name)
    "idx_16437_ix_protein_cazy" btree (cazy)
    "idx_16437_ix_protein_md5_aa" btree (md5_aa)
    "idx_16437_ix_protein_md5_cds" btree (md5_cds)
    "idx_16437_ix_protein_mibig" btree (mibig)
    "idx_16437_ix_protein_uniref" btree (uniref)
    "idx_16437_ix_protein_vfdb" btree (vfdb)
Foreign-key constraints:
    "protein_contig_id_fkey" FOREIGN KEY (contig_id) REFERENCES contig(name)
    "protein_ortholog_id_fkey" FOREIGN KEY (ortholog_id) REFERENCES ortholog(name)
Referenced by:
    TABLE "protein_antifam_association" CONSTRAINT "protein_antifam_association_protein_id_fkey" FOREIGN KEY (protein_id) REFERENCES protein(name)
    TABLE "protein_enzyme_association" CONSTRAINT "protein_enzyme_association_protein_id_fkey" FOREIGN KEY (protein_id) REFERENCES protein(name)
    TABLE "protein_kofam_association" CONSTRAINT "protein_kofam_association_protein_id_fkey" FOREIGN KEY (protein_id) REFERENCES protein(name)
    TABLE "protein_ncbifam_amr_association" CONSTRAINT "protein_ncbifam_amr_association_protein_id_fkey" FOREIGN KEY (protein_id) REFERENCES protein(name)
    TABLE "protein_pfam_association" CONSTRAINT "protein_pfam_association_protein_id_fkey" FOREIGN KEY (protein_id) REFERENCES protein(name)
```

## Querying PostgreSQL Data as a Graph with PuppyGraph
NOTE: This is still in development and does not currently
### Create a `docker-compose.yaml`

```yaml
services:
  puppygraph:
    image: puppygraph/puppygraph:stable
    pull_policy: always
    container_name: puppygraph
    environment:
      # PuppyGraph internal user/pass (for accessing PuppyGraph UI/API)
      - PUPPYGRAPH_USERNAME=puppygraph
      - PUPPYGRAPH_PASSWORD=puppygraph123

      # --- Configuration for YOUR PostgreSQL Database on the HOST ---
      - PUPPYGRAPH_DB_TYPE=postgres
      - PUPPYGRAPH_DB_HOST=host.docker.internal # Special DNS for host from container
      - PUPPYGRAPH_DB_PORT=5432                # Your host PG port
      - PUPPYGRAPH_DB_NAME=veba-essentials-database # <<< CORRECT DB NAME
      - PUPPYGRAPH_DB_USERNAME=veba               # Your PG user
      - PUPPYGRAPH_DB_PASSWORD=hello-postgresql   # Your PG user's password
      # Optional: Specify schema if not 'public'
      # - PUPPYGRAPH_DB_SCHEMA=public
    ports:
      # Map host ports to container ports (adjust host ports if needed)
      - "8081:8081" # PuppyGraph Web UI -> Use 8085:8081 if 8081 is busy on host
      - "8182:8182" # PuppyGraph HTTP API
      - "7687:7687" # PuppyGraph Bolt Port -> Use 7688:7687 if 7687 is busy on host

# No 'postgres' service defined here
# No custom network is strictly needed unless 'host.docker.internal' doesn't work
```

### Run PuppyGraph

```
sudo docker compose up -d
```