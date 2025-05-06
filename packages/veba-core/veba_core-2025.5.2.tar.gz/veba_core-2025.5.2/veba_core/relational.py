import os
import glob
import traceback
import hashlib
import json
# from types import SimpleNamespace
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import pyfastx
from pyexeggutor import open_file_reader
import sqlalchemy
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, Text,
    ForeignKey, Table, UniqueConstraint, inspect as sqla_inspect # Renamed inspect
)
from sqlalchemy.dialects.postgresql import ARRAY # Example if using PostgreSQL arrays instead of M2M
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Query, Session, RelationshipProperty, object_mapper

def md5hash(seq:str):
    seq = seq.lower()
    return hashlib.md5(seq.encode('utf-8')).hexdigest()

def md5hash_casesensitive(seq:str):
    return hashlib.md5(seq.encode('utf-8')).hexdigest()
    
def compile_genome_data(veba_essentials_directory: str):
    """
    Compile genome metadata from multiple sources into a single DataFrame.

    This function reads genome identifier mappings, taxonomy classifications, and genome statistics
    from specified subdirectories within the provided essentials directory. It filters out
    entries corresponding to plastid and mitochondrial genomes, then merges the data into a single
    pandas DataFrame.

    Parameters
    ----------
    veba_essentials_directory : str
        The path to the root directory containing the 'clustering', 'taxonomy_classification',
        and 'statistics' subdirectories with the required genome metadata files.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with genome taxonomy, identifier mapping, and statistics combined.
        The index consists of genome identifiers.
    """
    # Identifier mapping from clustering
    df_identifier_mapping = pd.read_csv(
        os.path.join(veba_essentials_directory, "clustering", "identifier_mapping.genomes.tsv.gz"),
        sep="\t", index_col=0
    )

    # Representatives
    representative_filepaths = glob.glob(
        os.path.join(veba_essentials_directory, "clustering", "representatives", "*.representatives.tsv")
    )
    df_representatives = pd.concat(
        list(map(lambda filepath: pd.read_csv(filepath, sep="\t", index_col=0), representative_filepaths))
    )["representative"].to_frame("representative")

    # Taxonomy
    taxonomy_filepaths = glob.glob(
        os.path.join(veba_essentials_directory, "taxonomy_classification", "*", "taxonomy.tsv.gz")
    )
    df_taxonomy = pd.concat(
        list(map(lambda filepath: pd.read_csv(filepath, sep="\t", index_col=0).iloc[:, 0], taxonomy_filepaths))
    ).to_frame("taxonomy")

    # Statistics
    df_statistics_genomes = pd.read_csv(
        os.path.join(veba_essentials_directory, "statistics", "genome_statistics.tsv.gz"),
        sep="\t", index_col=0
    )
    df_statistics_genomes = df_statistics_genomes.loc[
        df_statistics_genomes.index.map(lambda x: not x.startswith(("plastid/", "mitochondrion/")))
    ]

    # This only works for prokaryotic/viral organisms
    # df_statistics_cds = pd.read_csv(
    #     os.path.join(veba_essentials_directory, "statistics", "gene_statistics.cds.tsv.gz"),
    #     sep="\t", index_col=0
    # )
    # df_statistics_cds = df_statistics_cds.loc[df_statistics_genomes.index]
    # df_statistics_genomes["coding_density"] = df_statistics_cds["sum_len"]/df_statistics_genomes["sum_len"]

    # Quality
    genome_to_quality = dict()
    for organism_type in df_identifier_mapping["organism_type"].unique():
        if organism_type in {"prokaryotic", "viral"}:
            df_quality = pd.read_csv(os.path.join(veba_essentials_directory, "quality", f"quality.{organism_type}.tsv.gz"), sep="\t", index_col=0)
            df_quality.columns = df_quality.columns.map(str.lower) # Handles change from 2.4.x -> 2.5.x
            genome_to_quality.update(df_quality[["completeness", "contamination"]].T.to_dict())
        elif organism_type == "eukaryotic":
            df_quality = pd.read_csv(os.path.join(veba_essentials_directory, "quality", f"quality.{organism_type}.tsv.gz"), sep="\t", index_col=0, header=[0,1])
            for id_genome, row in df_quality.iterrows():
                row = row.dropna()
                level_0 = "generic"
                if "specific" in df_quality.columns.get_level_values(0):
                    level_0 = "specific"
                completeness = row[(level_0, "Complete")]
                contamination = row[(level_0, "Multi copy")]
                genome_to_quality[id_genome] = {"completeness":completeness, "contamination":contamination}
    df_quality = pd.DataFrame(genome_to_quality).T
    return pd.concat([df_taxonomy, df_identifier_mapping, df_statistics_genomes, df_quality, df_representatives], axis=1)


def reset_database(engine):
    """
    Drops all tables defined in the Base metadata and recreates them.
    WARNING: This deletes ALL data permanently.

    Args:
        engine: The SQLAlchemy engine instance.
    """
    print("WARNING: Dropping all tables and recreating schema...")
    try:
        # Drop all tables associated with the Base metadata
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped successfully.")

        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        print("Tables recreated successfully.")
        print("Database has been reset to an empty schema.")
    except Exception as e:
        print(f"An error occurred during database reset: {e}")
        # Depending on the error, the DB might be in an inconsistent state
        # You might need manual intervention or fixes to your models/setup
        

# # --- Database Summary Function ---
# def database_summary(session_factory):
#     """
#     Connects to the database using the provided session factory,
#     queries the count of objects in each table, and prints the summary.

#     Args:
#         session_factory: A configured SQLAlchemy sessionmaker instance (like SessionLocal).
#     """
#     with session_factory() as db: # Get a session from the factory
#         try:
#             model_to_count = dict()
#             models_to_summarize = [
#                 Sample, Pangenome, Genome, Ortholog, Contig, Protein,
#                 Pfam, KOfam, NCBIfamAMR, AntiFam, Enzyme # Lookup tables
#             ]
#             for model in models_to_summarize:
#                 count = db.query(model).count()
#                 model_to_count[model.__tablename__] = count
#             return pd.Series(model_to_count)
#         except Exception as e:
#             Exception(f"An error occurred while querying the database: {e}")

    
# --- Base Class ---
Base = declarative_base()

# --- Association Tables for Protein Many-to-Many Relationships ---
# NOTE: Foreign keys now point to STRING primary keys in Protein and Lookup tables

# Protein <-> Pfam
protein_pfam_association = Table(
    'protein_pfam_association', Base.metadata,
    # Changed Integer to String, updated ForeignKey target column
    Column('protein_id', String, ForeignKey('protein.name'), primary_key=True),
    Column('pfam_id', String, ForeignKey('pfam.name'), primary_key=True)
)

# Protein <-> Kofam
protein_kofam_association = Table(
    'protein_kofam_association', Base.metadata,
    Column('protein_id', String, ForeignKey('protein.name'), primary_key=True),
    Column('kofam_id', String, ForeignKey('kofam.name'), primary_key=True)
)

# Protein <-> NCBIFamAMR
protein_ncbifam_amr_association = Table(
    'protein_ncbifam_amr_association', Base.metadata,
    Column('protein_id', String, ForeignKey('protein.name'), primary_key=True),
    Column('ncbifam_amr_id', String, ForeignKey('ncbifam_amr.name'), primary_key=True)
)

# Protein <-> AntiFam
protein_antifam_association = Table(
    'protein_antifam_association', Base.metadata,
    Column('protein_id', String, ForeignKey('protein.name'), primary_key=True),
    Column('antifam_id', String, ForeignKey('antifam.name'), primary_key=True)
)

# Protein <-> Enzyme
protein_enzyme_association = Table(
    'protein_enzyme_association', Base.metadata,
    Column('protein_id', String, ForeignKey('protein.name'), primary_key=True),
    Column('enzyme_id', String, ForeignKey('enzyme.name'), primary_key=True)
)


# --- Lookup Tables for Protein Annotations ---
# Simplified: Using the 'name' (the string identifier itself) as the primary key

class Pfam(Base):
    __tablename__ = 'pfam'
    name = Column(String, primary_key=True, index=True) # e.g., "PF00001.1" should I use non-versioned Pfam id like PF00001? 
    accession = Column(String, primary_key=False, index=True) 
    description = Column(String, index=False)

    # Relationship uses the association table defined above
    proteins = relationship("Protein", secondary=protein_pfam_association, back_populates="pfams")

    def __repr__(self):
        return f"<Pfam(name='{self.name}', description='{self.description}')>"

class KOfam(Base):
    __tablename__ = 'kofam'
    # Using the name itself as the primary key
    name = Column(String, primary_key=True, index=True) # e.g., "K01234"
    description = Column(String, index=False)
    proteins = relationship("Protein", secondary=protein_kofam_association, back_populates="kofams")

    def __repr__(self):
        return f"<KOfam(name='{self.name}', description='{self.description}')>"

class NCBIfamAMR(Base):
    __tablename__ = 'ncbifam_amr'
    # Using the name itself as the primary key
    name = Column(String, primary_key=True, index=True)
    proteins = relationship("Protein", secondary=protein_ncbifam_amr_association, back_populates="ncbifam_amrs")

    def __repr__(self):
        return f"<NCBIfamAMR(name='{self.name}')>"

class AntiFam(Base):
    __tablename__ = 'antifam'
    # Using the name itself as the primary key
    name = Column(String, primary_key=True, index=True)
    proteins = relationship("Protein", secondary=protein_antifam_association, back_populates="antifams")

    def __repr__(self):
        return f"<AntiFam(name='{self.name}')>"

class Enzyme(Base):
    __tablename__ = 'enzyme'
    # Using the name itself as the primary key
    name = Column(String, primary_key=True, index=True) # e.g., EC number "1.1.1.1"
    proteins = relationship("Protein", secondary=protein_enzyme_association, back_populates="enzymes")

    def __repr__(self):
        return f"<Enzyme(name='{self.name}')>"


# --- Main Entity Classes ---

class Sample(Base):
    __tablename__ = 'sample'
    name = Column(String, primary_key=True)

    genomes = relationship("Genome", back_populates="sample")

    def __repr__(self):
        return f"<Sample(name='{self.name}')>" # Use quotes for string ID

class Pangenome(Base):
    __tablename__ = 'pangenome'
    # Changed primary key to String
    name = Column(String, primary_key=True)
    taxonomy = Column(String)

    genomes = relationship("Genome", back_populates="pangenome")
    orthologs = relationship("Ortholog", back_populates="pangenome")

    def __repr__(self):
        # Use quotes for string ID
        return f"<Pangenome(name='{self.name}', taxonomy='{self.taxonomy}')>"


class Ortholog(Base):
    __tablename__ = 'ortholog'
    name = Column(String, primary_key=True)
    product = Column(String, nullable=True)

    pangenome_id = Column(String, ForeignKey('pangenome.name'), nullable=False)
    pangenome = relationship("Pangenome", back_populates="orthologs")

    proteins = relationship("Protein", back_populates="ortholog")

    def __repr__(self):
        # Use quotes for string IDs
        return f"<Ortholog(name='{self.name}', product='{self.product}')>"


class Genome(Base):
    __tablename__ = 'genome'
    # Changed primary key to String
    name = Column(String, primary_key=True)
    taxonomy = Column(String)
    organism_type = Column(String)
    completeness = Column(Float)
    contamination = Column(Float)
    coding_density = Column(Float)
    gc_content = Column(Float)
    size = Column(Integer)
    n50 = Column(Float)
    is_pangenome_representative = Column(Boolean, default=False)
    path_assembly = Column(String)
    path_cds = Column(String)
    path_aa = Column(String)

    # Changed ForeignKey type to String
    sample_id = Column(String, ForeignKey('sample.name'), nullable=False)
    sample = relationship("Sample", back_populates="genomes")

    # Changed ForeignKey type to String
    pangenome_id = Column(String, ForeignKey('pangenome.name'), nullable=True)
    pangenome = relationship("Pangenome", back_populates="genomes")

    contigs = relationship("Contig", back_populates="genome", cascade="all, delete-orphan")

    def __repr__(self):
         # Use quotes for string IDs
        return f"<Genome(name='{self.name}', taxonomy='{self.taxonomy}')>"


class Contig(Base):
    __tablename__ = 'contig'
    name = Column(String, primary_key=True)
    sequence = Column(Text)
    length = Column(Integer) 
    md5 = Column(String, index=True) 

    # Changed ForeignKey type to String
    genome_id = Column(String, ForeignKey('genome.name'), nullable=False)
    genome = relationship("Genome", back_populates="contigs")

    proteins = relationship("Protein", back_populates="contig", cascade="all, delete-orphan")

    def __repr__(self):
         # Use quotes for string IDs
        # if self.length:
        return f"<Contig(name='{self.id_node}', length={self.length}, genome_id='{self.genome_id}')>"
        # else:
            # return f"<Contig(id='{self.id_contig}', genome_id='{self.genome_id}')>"



class Protein(Base):
    __tablename__ = 'protein'
    databasename_to_attributename = {
    "UniRef":"uniref",
    "MIBiG":"mibig",
    "VFDB":"vfdb",
    "CAZy":"cazy",
    "Pfam":"pfams",
    "KOfam":"kofams",
    "NCBIfam-AMR":"ncbifam_amrs",
    "AntiFam":"antifams",
    "Enzymes":"enzymes",
    }

    diamond_databases = ["uniref", "mibig", "vfdb", "cazy"]
    hmm_databases = ["pfams", "kofams", "ncbifam_amrs", "antifams", "enzymes"]
    
    # Changed primary key to String
    name = Column(String, primary_key=True)
    cds = Column(Text, nullable=True)
    aa = Column(Text, nullable=True)
    md5_cds = Column(String, nullable=True, index=True) # Should I index this?
    md5_aa = Column(String, nullable=True, index=True) # Should I index this?
    length = Column(Integer)
    
    product = Column(String, nullable=True)
    uniref = Column(String, nullable=True, index=True)
    mibig = Column(String, nullable=True, index=True)
    vfdb = Column(String, nullable=True, index=True)
    cazy = Column(String, nullable=True, index=True)

    # Changed ForeignKey type to String
    contig_id = Column(String, ForeignKey('contig.name'), nullable=False)
    contig = relationship("Contig", back_populates="proteins")

    # Changed ForeignKey type to String
    ortholog_id = Column(String, ForeignKey('ortholog.name'), nullable=True)
    ortholog = relationship("Ortholog", back_populates="proteins")

    # Relationships use the updated association tables
    pfams = relationship("Pfam", secondary=protein_pfam_association, back_populates="proteins")
    kofams = relationship("KOfam", secondary=protein_kofam_association, back_populates="proteins")
    ncbifam_amrs = relationship("NCBIfamAMR", secondary=protein_ncbifam_amr_association, back_populates="proteins")
    antifams = relationship("AntiFam", secondary=protein_antifam_association, back_populates="proteins")
    enzymes = relationship("Enzyme", secondary=protein_enzyme_association, back_populates="proteins")

    def append_hmms(self, database_name, hmms):
        db_attribute = self.databasename_to_attributename[database_name]
        for hmm in hmms:
            getattr(self, db_attribute).append(hmm)
            
            
    def __repr__(self):
        # Use quotes for string IDs
        return f"<Protein(name='{self.name}', product='{self.product}')>"

# class Compound(Base):
# class Reaction(Base):

# # --- Database Setup ---
# def setup_database(database_url):
#     """Creates the engine and tables."""
#     engine = create_engine(database_url, echo=False) # Turn echo off for cleaner output usually
#     Base.metadata.create_all(engine)
#     print(f"Database tables created for {database_url}")
#     return engine

    
class VEBAEssentialsDatabase:
    """
    Manages the creation, population, and interaction with the VEBA Essentials database.
    """
    HMM_DATABASE_NAME_TO_CLASS = { # Corrected name if needed
        "Pfam": Pfam, "NCBIfam-AMR": NCBIfamAMR, "KOfam": KOfam,
        "Enzymes": Enzyme, "AntiFam": AntiFam,
    }
    DATABASE_NAME_TO_ATTRIBUTE_NAME = {
        "UniRef": "uniref", "MIBiG": "mibig", "VFDB": "vfdb", "CAZy": "cazy",
        "Pfam": "pfams", "KOfam": "kofams", "NCBIfam-AMR": "ncbifam_amrs",
        "AntiFam": "antifams", "Enzymes": "enzymes",
    }
    MODELS_FOR_SCHEMA = [
        Sample, Pangenome, Genome, Ortholog, Contig, Protein,
        Pfam, KOfam, NCBIfamAMR, AntiFam, Enzyme
    ]
    
    def __init__(self, database_url: str, veba_essentials_directory: str, store_sequences: bool = True, name: str = None):
        self.database_url = database_url
        self.veba_essentials_directory = veba_essentials_directory
        self.store_sequences = store_sequences
        self.name = name
        self.engine = create_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print(f"Database controller initialized for: {self.database_url}")

    def setup_schema(self):
        """Creates all database tables defined by the Base metadata."""
        print(f"Setting up database schema for {self.database_url}...")
        Base.metadata.create_all(bind=self.engine)
        print("Database schema setup complete.")

    def reset_schema(self):
        """Drops all tables and recreates the schema. WARNING: Deletes all data."""
        reset_database(self.engine) # Use the existing global reset_database function

    def database_summary(self): # This is the method you call on the instance
        """Prints a summary of object counts in each table."""
        # Assuming the global function `print_database_summary` exists
        # and correctly queries/prints the summary.
        # If not, implement the logic here directly or call the correct global func.

        # Option 1: Call the global function if it exists and works
        # print_database_summary(self.SessionLocal)

        # Option 2: Implement the logic directly here (more self-contained)
        print("--- Database Object Summary ---")
        with self.SessionLocal() as db:
            model_to_count = {}
            try:
                inspector = sqla_inspect(self.engine)
                available_tables = inspector.get_table_names()
                print(f"Available tables for summary: {available_tables}")

                models_to_summarize = self.MODELS_FOR_SCHEMA # Use class attribute

                for model in models_to_summarize:
                    table_name = model.__tablename__
                    if table_name in available_tables:
                        try:
                            count = db.query(model).count()
                            print(f"- {table_name}: {count}")
                            model_to_count[table_name] = count
                        except Exception as count_err:
                             print(f"- {table_name}: ERROR counting - {count_err}")
                             model_to_count[table_name] = "ERROR"
                    else:
                        print(f"- {table_name}: Table not found!")
                        model_to_count[table_name] = "Not Found"
            except Exception as e:
                print(f"An error occurred while querying the database summary: {e}")
                traceback.print_exc()
            print("-----------------------------")
            # Optionally return the counts as a Series/Dict
            # return pd.Series(model_to_count)
            

    # def list_existing_genome_names(self) -> list[str]:
    #     """Queries the database and returns a list of all committed genome names."""
    #     existing_names = []
    #     with self.SessionLocal() as db:
    #         try:
    #             results = db.query(Genome.name).order_by(Genome.name).all()
    #             existing_names = [row[0] for row in results]
    #             print(f"Found {len(existing_names)} committed genome names in the database.")
    #         except Exception as e:
    #             print(f"Error querying existing genome names: {e}")
    #     return existing_names

    # --- Individual Population Methods (Mostly unchanged, session passed in) ---

    def _populate_samples(self, db: Session, df_genome_data: pd.DataFrame):
        """Adds Sample objects to the database session."""
        print("Populating samples...")
        added_count = 0
        skipped_count = 0
        samples = df_genome_data["sample_of_origin"].unique()
        for name in tqdm(samples, desc="Adding samples", unit=" samples"):
            # Check within the current session first (identity map)
            sample_in_session = db.query(Sample).filter(Sample.name == name).with_for_update().first()
            if not sample_in_session:
                sample = Sample(name=name)
                db.add(sample)
                added_count += 1
            else:
                skipped_count += 1
        print(f"Samples populated (Added: {added_count}, Skipped Existing: {skipped_count}).")

    def _populate_pangenomes(self, db: Session, df_genome_data: pd.DataFrame) -> dict:
        """Adds Pangenome objects and returns a map {pg_id: pangenome_obj}."""
        print("Populating pangenomes...")
        pangenome_ids = df_genome_data['id_genome_cluster'].unique()
        pangenome_map = {}
        added_count = 0
        skipped_count = 0
        print(f"Found {len(pangenome_ids)} unique pangenome IDs.")
        for pg_id in tqdm(pangenome_ids, desc="Adding Pangenomes", unit=" pangenomes"):
            if pd.isna(pg_id): continue # Skip if no pangenome ID

            existing_pg = db.query(Pangenome).filter(Pangenome.name == pg_id).with_for_update().first()
            if not existing_pg:
                rep_genome_row = df_genome_data[(df_genome_data['id_genome_cluster'] == pg_id) & (df_genome_data['representative'] == True)]
                taxonomy = rep_genome_row['taxonomy'].iloc[0] if not rep_genome_row.empty else None
                pangenome = Pangenome(name=pg_id, taxonomy=taxonomy)
                db.add(pangenome)
                pangenome_map[pg_id] = pangenome
                added_count += 1
            else:
                pangenome_map[pg_id] = existing_pg
                skipped_count += 1
        print(f"Pangenomes populated (Added: {added_count}, Skipped Existing: {skipped_count}).")
        return pangenome_map

    def _populate_orthologs(self, db: Session, df_ortholog_annotations: pd.DataFrame):
        """Adds Ortholog objects, linking to Pangenomes if possible."""
        print("Populating orthologs...")
        # Assumes ('Identifiers', 'id_genome_cluster') maps ortholog to pangenome
        ortholog_data = df_ortholog_annotations.copy() # Avoid modifying original
        # Ensure correct column names based on your actual file structure
        ortholog_col = ('Identifiers', 'id_protein_cluster') # Adjust if needed
        pangenome_col = ('Identifiers', 'id_genome_cluster') # Adjust if needed
        product_col = ('Consensus', 'composite_name') # Adjust if needed

        # Check if columns exist
        if pangenome_col not in ortholog_data.columns or product_col not in ortholog_data.columns:
             print(f"Warning: Expected columns {pangenome_col} or {product_col} not found in ortholog annotations. Cannot link pangenomes or products.")
             # Handle appropriately - maybe create orthologs without links?

        added_count = 0
        skipped_count = 0
        linked_count = 0
        unlinked_count = 0

        for og_id, row in tqdm(ortholog_data.iterrows(), desc="Adding Orthologs", total=len(ortholog_data), unit=" orthologs"):
            if pd.isna(og_id): continue

            existing_og = db.query(Ortholog).filter(Ortholog.name == og_id).with_for_update().first()
            if not existing_og:
                pangenome_id_for_og = row.get(pangenome_col, None) if pangenome_col in row else None
                product = row.get(product_col, None) if product_col in row else None

                # Check if the referenced Pangenome exists IN THE DATABASE (must be committed)
                pangenome_exists = False
                if pd.notna(pangenome_id_for_og):
                   pangenome_exists = db.query(Query(Pangenome).filter(Pangenome.name == pangenome_id_for_og).exists()).scalar()

                if pangenome_exists:
                    ortholog = Ortholog(name=og_id,
                                        product=product if pd.notnull(product) else None,
                                        pangenome_id=pangenome_id_for_og)
                    db.add(ortholog)
                    added_count += 1
                    linked_count += 1
                else:
                    # Ortholog depends on Pangenome (nullable=False). Cannot add without it.
                    print(f"Warning: Pangenome '{pangenome_id_for_og}' for Ortholog {og_id} not found in DB. Skipping Ortholog.")
                    unlinked_count += 1
                    # If pangenome_id was nullable=True, you could add it unlinked:
                    # ortholog = Ortholog(name=og_id, product=product if pd.notnull(product) else None)
                    # db.add(ortholog)
                    # added_count += 1
                    # unlinked_count += 1

            else:
                skipped_count += 1

        print(f"Orthologs populated (Added: {added_count} [Linked: {linked_count}, Unlinked/Skipped: {unlinked_count}], Skipped Existing: {skipped_count}).")


    def _ensure_hmm_objects(self, db: Session, query_hmms: dict, hmm_to_description: dict):
        """Checks for existing HMM objects, creates new ones. Returns map of ID to object."""
        print("Populating HMM lookup tables...")
        hmm_id_to_object = {}
        total_added = 0
        total_existing = 0
        for hmm_db_name, ids in tqdm(query_hmms.items(), desc="Ensuring HMM objects", unit=" HMM DBs"):
            if not ids: continue # Skip if no IDs for this DB
            HMMClass = self.HMM_DATABASE_NAME_TO_CLASS[hmm_db_name]

            # Fetch existing HMMs for this database in bulk
            existing_hmms = db.query(HMMClass).filter(HMMClass.name.in_(ids)).all()
            existing_hmm_map = {hmm.name: hmm for hmm in existing_hmms}
            hmm_id_to_object.update(existing_hmm_map)
            total_existing += len(existing_hmm_map)

            # Identify and create missing HMMs
            missing_ids = ids - set(existing_hmm_map.keys())
            new_hmm_objects = []
            for id_hmm in missing_ids:
                attrs = {'name': id_hmm}
                description = hmm_to_description.get(id_hmm)
                if description and hasattr(HMMClass, 'description'):
                    attrs['description'] = description
                if hmm_db_name == "Pfam" and hasattr(HMMClass, 'accession'):
                     if hasattr(HMMClass, 'accession'):
                        attrs['accession'] = id_hmm.split(".")[0]
                     # Use description from dict if available
                     if description: attrs['description'] = description

                new_hmm = HMMClass(**attrs)
                new_hmm_objects.append(new_hmm)
                hmm_id_to_object[id_hmm] = new_hmm # Add to map

            if new_hmm_objects:
                db.add_all(new_hmm_objects)
                total_added += len(new_hmm_objects)

        print(f"HMM objects ensured (Added: {total_added}, Found Existing: {total_existing}).")
        return hmm_id_to_object


    def _populate_genomes(self, db: Session, df_genome_data: pd.DataFrame):
        """Adds Genome objects, linking to committed Samples and Pangenomes."""
        print("Populating genomes...")
        genome_data_columns = ["taxonomy", "organism_type", "sample_of_origin", "id_genome_cluster", "sum_len", "N50", "GC(%)", "completeness", "contamination", "representative"]
        added_count = 0
        skipped_count = 0
        link_error_count = 0

        # Fetch existing sample and pangenome names for faster checks
        valid_sample_names = {s.name for s in db.query(Sample.name).all()}
        valid_pangenome_names = {p.name for p in db.query(Pangenome.name).all()}

        for name, row in tqdm(df_genome_data.loc[:, genome_data_columns].iterrows(), desc="Adding genomes", unit=" genomes", total=len(df_genome_data)):
            existing_genome = db.query(Genome).filter(Genome.name == name).with_for_update().first()
            if not existing_genome:
                # --- Validate Foreign Keys ---
                sample_id = row["sample_of_origin"]
                pangenome_id = row["id_genome_cluster"]
                sample_ok = sample_id in valid_sample_names
                # Pangenome link is nullable, so it's okay if it's missing or NaN
                pangenome_ok = pd.isna(pangenome_id) or pangenome_id in valid_pangenome_names

                if not sample_ok:
                    print(f"Warning: Sample '{sample_id}' for Genome {name} not found in DB. Skipping Genome.")
                    link_error_count += 1
                    continue
                # If pangenome FK were not nullable, add:
                # if not pangenome_ok:
                #    print(f"Warning: Pangenome '{pangenome_id}' for Genome {name} not found in DB. Skipping Genome.")
                #    link_error_count += 1
                #    continue
                # --- End Validation ---

                attributes = dict(
                    name=name,
                    taxonomy=row["taxonomy"],
                    organism_type=row["organism_type"],
                    completeness=row["completeness"],
                    contamination=row["contamination"],
                    size=row["sum_len"],
                    gc_content=row["GC(%)"],
                    n50=row["N50"],
                    pangenome_id=pangenome_id if pangenome_ok and pd.notna(pangenome_id) else None, # Assign FK directly
                    sample_id=sample_id, # Assign FK directly
                    is_pangenome_representative=row["representative"],
                )
                genome = Genome(**attributes)
                db.add(genome)
                added_count += 1
            else:
                 skipped_count += 1
        print(f"Genomes populated (Added: {added_count}, Skipped Existing: {skipped_count}, Link Errors: {link_error_count}).")

    def _update_genome_paths(self, db: Session):
        """Updates path_aa and path_cds for existing Genome objects."""
        print("Updating genome sequence file paths...")
        updated_aa_count = 0
        updated_cds_count = 0
        genome_not_found_count = 0
    
        # Fetch existing genomes once for potential lookup (might be large)
        # Alternatively, query inside the loop if memory is a concern
        # genome_map = {g.name: g for g in db.query(Genome).all()} # Potential high memory use
        # print(f"Fetched {len(genome_map)} genomes for path updates.")
    
        # Update AA Paths
        protein_filepaths = glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.faa.gz")) \
                          + glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.faa"))
        for filepath in tqdm(protein_filepaths, desc="Updating AA paths", unit=" files"):
            filename = os.path.basename(filepath)
            id_genome = None
            if filename.endswith(".faa.gz"): id_genome = filename[:-len(".faa.gz")]
            elif filename.endswith(".faa"): id_genome = filename[:-len(".faa")]
            else: continue # Skip files with unexpected extensions
    
            # Query for the specific genome now (guaranteed to exist if Stage 2 succeeded)
            genome_obj = db.query(Genome).filter(Genome.name == id_genome).first()
            if genome_obj:
                genome_obj.path_aa = filepath
                updated_aa_count += 1
            else:
                print(f"Warning: Genome '{id_genome}' not found during AA path update (from {filename}).")
                genome_not_found_count +=1
    
    
        # Update CDS Paths
        cds_filepaths = glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.ffn.gz")) \
                      + glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.ffn"))
        for filepath in tqdm(cds_filepaths, desc="Updating CDS paths", unit=" files"):
            filename = os.path.basename(filepath)
            id_genome = None
            if filename.endswith(".ffn.gz"): id_genome = filename[:-len(".ffn.gz")]
            elif filename.endswith(".ffn"): id_genome = filename[:-len(".ffn")]
            else: continue # Skip
    
            genome_obj = db.query(Genome).filter(Genome.name == id_genome).first()
            if genome_obj:
                genome_obj.path_cds = filepath
                updated_cds_count += 1
            else:
                # This might be redundant if already warned above, but good for clarity
                if id_genome: # Avoid warning if id_genome couldn't be parsed
                    print(f"Warning: Genome '{id_genome}' not found during CDS path update (from {filename}).")
                    # Increment only if not already counted
                    # genome_not_found_count +=1 # Avoid double counting
    
        print(f"Genome paths updated (AA: {updated_aa_count}, CDS: {updated_cds_count}, Genomes Not Found: {genome_not_found_count}).")
    def _populate_contigs(self, db: Session):
        """Adds Contig objects, linking to committed Genomes."""
        print("Populating contigs...")
        genome_files = glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.fa.gz"))
        added_count = 0
        skipped_count = 0
        genome_missing_count = 0

        # Fetch existing genome names for faster checks
        valid_genome_names = {g.name for g in db.query(Genome.name).all()}

        for filepath in tqdm(genome_files, desc="Adding contigs", unit=" genomes"):
            # Robustly extract genome ID (handle potential variations if needed)
            filename = os.path.basename(filepath)
            if filename.endswith(".fa.gz"):
                 id_genome = filename[:-len(".fa.gz")]
            # Add other potential extensions if necessary
            # elif filename.endswith(".fasta.gz"):
            #      id_genome = filename[:-len(".fasta.gz")]
            else:
                 print(f"Warning: Unexpected filename format {filename}. Cannot determine genome ID. Skipping file.")
                 continue

            # Check if genome exists IN THE DATABASE (committed)
            genome_exists = id_genome in valid_genome_names
            genome_obj = db.query(Genome).filter(Genome.name == id_genome).first()
            
            if not genome_exists:
                # This check is now more reliable
                print(f"Warning: Genome {id_genome} not found (expected from {filename}). Skipping contigs.")
                genome_missing_count += 1
                continue
            else:
                genome_obj.path_assembly = filepath

            for name, seq in pyfastx.Fasta(filepath, build_index=False):
                existing_contig = db.query(Contig).filter(Contig.name == name).with_for_update().first()
                if not existing_contig:
                    attributes = dict(
                        name=name,
                        genome_id=id_genome, # Assign FK directly
                        length=len(seq),
                    )
                    if self.store_sequences:
                        attributes["sequence"] = seq
                    attributes["md5"] = md5hash(seq)
                    contig = Contig(**attributes)
                    db.add(contig)
                    added_count += 1
                else:
                    skipped_count += 1
        print(f"Contigs populated (Added: {added_count}, Skipped Existing: {skipped_count}, Genome Not Found Errors: {genome_missing_count}).")


    def _parse_protein_data(self, df_protein_annotations: pd.DataFrame) -> tuple:
         """Parses annotation DF into structured dictionaries."""
         print("Parsing protein annotations structure...")
         protein_to_attributes = {}
         protein_to_hmm_ids = defaultdict(lambda: defaultdict(list)) # {prot_id: {hmm_db_name: [id1, id2]}}
         query_hmms = defaultdict(set) # {hmm_db_name: {id1, id2}}
         hmm_to_description = {}

         for id_protein, row in tqdm(df_protein_annotations.iterrows(), desc="Parsing protein annotations", unit=" proteins", total=len(df_protein_annotations)):
            contig_id = id_protein.rsplit("_", maxsplit=1)[0]
            ortholog_id = row.get(("Identifiers", "id_protein_cluster"), None)

            attributes = {'name': id_protein, 'contig_id': contig_id, 'ortholog_id': ortholog_id}
            product = row.get(("Consensus", "composite_name"), None)
            if pd.notnull(product): attributes["product"] = product

            for diamond_db_name in ["UniRef", "MIBiG", "VFDB", "CAZy"]:
                value = row.get((diamond_db_name, "sseqid"), None)
                if pd.notnull(value):
                    attributes[self.DATABASE_NAME_TO_ATTRIBUTE_NAME[diamond_db_name]] = value

            for hmm_db_name in self.HMM_DATABASE_NAME_TO_CLASS.keys():
                try:
                    ids_str = row.get((hmm_db_name, "ids"), "[]"); names_str = row.get((hmm_db_name, "names"), "[]")
                    ids = eval(ids_str) if pd.notnull(ids_str) else []; names = eval(names_str) if pd.notnull(names_str) else []
                except Exception as e: ids, names = [], [] # Handle parse errors
                if ids:
                    query_hmms[hmm_db_name].update(ids)
                    protein_to_hmm_ids[id_protein][hmm_db_name].extend(ids)
                    if names: hmm_to_description.update(dict(zip(ids, names)))

            protein_to_attributes[id_protein] = attributes
         return protein_to_attributes, protein_to_hmm_ids, query_hmms, hmm_to_description

    def _add_protein_sequences(self, protein_to_attributes: dict):
        """Adds AA and CDS sequences to the protein attributes dictionary if storing."""
        if not self.store_sequences:
             print("Skipping protein sequence loading (store_sequences=False).")
             return # Exit early if not storing
    
        print("Preparing protein AA/CDS sequences for attribute dictionary...")
        target_protein_ids = set(protein_to_attributes.keys()) # Use set for faster lookup
        count_aa, count_cds = 0, 0
    
        # AA sequences
        protein_filepaths = glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.faa.gz")) \
                          + glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.faa"))
        for filepath in tqdm(protein_filepaths, desc="Loading protein AA sequences", unit=" files"):
            try:
                for name, seq in pyfastx.Fasta(filepath, build_index=False):
                    if name in target_protein_ids:
                        protein_to_attributes[name]["aa"] = seq
                        protein_to_attributes[name]["md5_aa"] = md5hash(seq) # Calculate hash here
                        count_aa += 1
            except Exception as e:
                print(f"Error reading AA sequence file {filepath}: {e}")
        print(f"Prepared {count_aa} AA sequences for {len(target_protein_ids)} proteins.")
    
        # CDS sequences
        cds_filepaths = glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.ffn.gz")) \
                      + glob.glob(os.path.join(self.veba_essentials_directory, "genomes", "*", "*.ffn"))
        for filepath in tqdm(cds_filepaths, desc="Loading protein CDS sequences", unit=" files"):
            try:
                for name, seq in pyfastx.Fasta(filepath, build_index=False):
                    if name in target_protein_ids:
                        protein_to_attributes[name]["cds"] = seq
                        protein_to_attributes[name]["md5_cds"] = md5hash(seq) # Calculate hash here
                        # Assume length is based on AA sequence, or calculate if needed
                        if "aa" in protein_to_attributes[name]:
                           protein_to_attributes[name]["length"] = len(protein_to_attributes[name]["aa"])
                        count_cds += 1
            except Exception as e:
                 print(f"Error reading CDS sequence file {filepath}: {e}")
        print(f"Prepared {count_cds} CDS sequences.")

    def _populate_proteins_and_link_annotations(self, db: Session, protein_to_attributes: dict, protein_to_hmm_ids: dict):
        """Adds Protein objects, linking to committed Contigs, Orthologs, and HMM lookups."""
        print("Populating proteins and linking annotations...")
        added_count = 0
        skipped_count = 0
        link_error_count = 0

        # Fetch necessary FK object names/IDs for faster checks
        valid_contig_names = {c.name for c in db.query(Contig.name).all()}
        # Ortholog link is nullable, but fetch valid ones if needed for linking
        valid_ortholog_names = {o.name for o in db.query(Ortholog.name).all()}
        # Fetch all relevant HMM objects into memory for efficient linking
        hmm_object_cache = {} # {HMMClassName: {hmm_name: hmm_obj}}
        for hmm_cls in self.HMM_DATABASE_NAME_TO_CLASS.values():
            hmm_object_cache[hmm_cls.__name__] = {hmm.name: hmm for hmm in db.query(hmm_cls).all()}
            print(f"Cached {len(hmm_object_cache[hmm_cls.__name__])} objects for {hmm_cls.__name__}")

        for id_protein, attributes in tqdm(protein_to_attributes.items(), desc="Adding proteins", unit=" proteins"):
            existing_protein = db.query(Protein).filter(Protein.name == id_protein).with_for_update().first()
            if not existing_protein:
                # --- Validate Foreign Keys ---
                contig_id = attributes.get('contig_id')
                ortholog_id = attributes.get('ortholog_id') # Can be None/NaN

                contig_ok = contig_id in valid_contig_names
                # Ortholog is nullable, so only check if an ID is provided
                ortholog_ok = pd.isna(ortholog_id) or ortholog_id in valid_ortholog_names

                if not contig_ok:
                    print(f"Warning: Contig '{contig_id}' for Protein {id_protein} not found in DB. Skipping Protein.")
                    link_error_count += 1
                    continue
                if pd.notna(ortholog_id) and not ortholog_ok:
                     print(f"Warning: Ortholog '{ortholog_id}' for Protein {id_protein} provided but not found in DB. Setting link to NULL.")
                     # Adjust attributes dict if needed, though relationship assignment handles this
                     attributes['ortholog_id'] = None # Explicitly nullify FK if invalid

                # --- Create Protein ---
                # Assign FKs directly in attributes before creating
                attributes['contig_id'] = contig_id
                attributes['ortholog_id'] = ortholog_id if ortholog_ok and pd.notna(ortholog_id) else None

                protein = Protein(**attributes)

                # --- Link HMM relationships (M2M) ---
                protein_hmms = protein_to_hmm_ids.get(id_protein, {})
                for hmm_db_name, hmm_ids in protein_hmms.items():
                     if not hmm_ids: continue
                     HMMClass = self.HMM_DATABASE_NAME_TO_CLASS[hmm_db_name]
                     relationship_attr = self.DATABASE_NAME_TO_ATTRIBUTE_NAME[hmm_db_name]
                     hmm_cache_for_db = hmm_object_cache.get(HMMClass.__name__, {})
                     # Get actual HMM objects from cache
                     hmm_objects_to_link = [hmm_cache_for_db.get(hid) for hid in hmm_ids if hmm_cache_for_db.get(hid)]
                     if hmm_objects_to_link:
                         # Use SQLAlchemy's relationship append
                         getattr(protein, relationship_attr).extend(hmm_objects_to_link)
                     else:
                         print(f"Warning: No valid HMM objects found in cache for protein {id_protein}, db {hmm_db_name}, ids {hmm_ids}")


                db.add(protein)
                added_count += 1
            else:
                 skipped_count += 1
                 # TODO: Implement update logic if needed - fetch existing protein and update fields/relationships

        print(f"Proteins populated (Added: {added_count}, Skipped Existing: {skipped_count}, Link Errors: {link_error_count}).")


    # --- Master Population Method ---
    def populate_all(self, reset_first: bool = False):
        """
        Runs all population steps in order, committing after major stages.
        """
        # --- Initial Setup ---
        try:
            if reset_first:
                self.reset_schema() # Use instance method
            else:
                self.setup_schema() # Use instance method
        except Exception as setup_err:
             print(f"FATAL: Schema setup/reset failed: {setup_err}. Stopping population.")
             traceback.print_exc()
             return

        print("\n--- Starting Full Database Population ---")

        # --- Load & Prepare Data ---
        print("Loading and preparing source data...")
        try:
            df_genome_data = compile_genome_data(self.veba_essentials_directory)
            protein_annot_path = os.path.join(self.veba_essentials_directory, "annotation", "annotations.proteins.tsv.gz")
            ortholog_annot_path = os.path.join(self.veba_essentials_directory, "annotation", "annotations.protein_clusters.tsv.gz")
            if not os.path.exists(protein_annot_path): raise FileNotFoundError(protein_annot_path)
            if not os.path.exists(ortholog_annot_path): raise FileNotFoundError(ortholog_annot_path)
            df_protein_annotations = pd.read_csv(protein_annot_path, sep="\t", index_col=0, header=[0,1], low_memory=False)
            df_ortholog_annotations = pd.read_csv(ortholog_annot_path, sep="\t", index_col=0, header=[0,1], low_memory=False)

            protein_to_attributes, protein_to_hmm_ids, query_hmms, hmm_to_description = self._parse_protein_data(df_protein_annotations)
            self._add_protein_sequences(protein_to_attributes)

        except FileNotFoundError as e: print(f"FATAL: Source data file not found: {e}. Stopping."); return
        except Exception as e: print(f"FATAL: Failed loading/parsing source data: {e}"); traceback.print_exc(); return

        # --- Transaction Stages ---
        stages = [
            ("Stage 1: Samples, Pangenomes, Orthologs, HMM Lookups", self._run_stage1),
            ("Stage 2: Genomes", self._run_stage2),
            ("Stage 2.5: Update Genome Paths", self._run_stage2_5),
            ("Stage 3: Contigs", self._run_stage3),
            ("Stage 4: Proteins & M2M Links", self._run_stage4)
        ]
        stage_args = {
            "_run_stage1": (df_genome_data, df_ortholog_annotations, query_hmms, hmm_to_description),
            "_run_stage2": (df_genome_data,),
            "_run_stage2_5": (),
            "_run_stage3": (),
            "_run_stage4": (protein_to_attributes, protein_to_hmm_ids)
        }

        overall_success = True # Start assuming success

        for stage_name, stage_runner in stages:
            if not overall_success: # Skip if a previous stage failed
                print(f"\nSkipping {stage_name} because a previous stage failed.")
                continue

            print(f"\n--- {stage_name} ---")
            with self.SessionLocal() as db:
                try:
                    args = stage_args.get(stage_runner.__name__, ())
                    stage_runner(db, *args) # Call the stage logic

                    print(f"Attempting to commit {stage_name}...")
                    db.commit() # Commit the changes for this stage
                    print(f"Commit successful for {stage_name}.")
                    print(f"--- {stage_name} Complete ---")
                    # If commit succeeds, overall_success remains True

                except Exception as e:
                    overall_success = False # Mark failure if any exception occurs in the stage
                    print(f"\n--- ERROR during {stage_name}: Rolling back changes for this stage ---")
                    print(f"Error details: {e}")
                    traceback.print_exc()
                    try:
                        db.rollback()
                        print("--- Rollback successful ---")
                    except Exception as rb_err:
                         print(f"--- CRITICAL ERROR during rollback attempt: {rb_err} ---")
                    print("--- Further population stages will be skipped. ---")
                    # Loop will continue, but subsequent stages will be skipped by the check at the top

        # Final status message based on the overall flag
        if overall_success:
            print("\n--- Database Population Finished Successfully ---")
        else:
             print("\n--- Database Population Finished With Errors In One Or More Stages ---")

        # Print final summary
        self.database_summary() # Call the instance method
    
    
    # --- Stage Runner Methods ---
    # These wrap the actual population logic for clarity in populate_all
    def _run_stage1(self, db: Session, df_genome_data, df_ortholog_annotations, query_hmms, hmm_to_description):
        self._populate_samples(db, df_genome_data)
        self._populate_pangenomes(db, df_genome_data)
        # Commit Samples and Pangenomes needed for Ortholog FKs
        db.flush(); print("Flushed Samples and Pangenomes...") # Flush after adding
        self._populate_orthologs(db, df_ortholog_annotations)
        self._ensure_hmm_objects(db, query_hmms, hmm_to_description)
        # Commit happens in populate_all after this method returns
    
    def _run_stage2(self, db: Session, df_genome_data):
        self._populate_genomes(db, df_genome_data)
        # Commit happens in populate_all
    
    # New stage runner for updating paths
    def _run_stage2_5(self, db: Session):
        self._update_genome_paths(db)
        # Commit happens in populate_all
    
    def _run_stage3(self, db: Session):
        self._populate_contigs(db)
        # Commit happens in populate_all
    
    def _run_stage4(self, db: Session, protein_to_attributes, protein_to_hmm_ids):
        self._populate_proteins_and_link_annotations(db, protein_to_attributes, protein_to_hmm_ids)
        # Commit happens in populate_all
        
    def to_schema(self, path: str = None, format: str = "puppygraph"):
        """
        Generates a JSON schema representation of the SQLAlchemy models.

        Args:
            path (str, optional): File path to write the JSON schema to.
                                   If None, returns the JSON string. Defaults to None.
            format (str, optional): The target format (currently only supports
                                    "puppygraph" - a generic node/edge format).
                                    Defaults to "puppygraph".

        Returns:
            str | None: The JSON schema as a string if path is None, otherwise None.

        Raises:
            ValueError: If an unsupported format is requested.
            IOError: If writing to the specified path fails.
        """
        if format.lower() != "puppygraph":
            raise ValueError(f"Unsupported schema format: '{format}'. Only 'puppygraph' is supported.")

        print(f"Generating '{format}' schema...")
        schema_nodes = []
        schema_edges = []
        processed_relationships = set() # To avoid duplicates from back_populates

        # Helper to map SQLAlchemy types to simple strings
        def map_type(sqla_type):
            type_map = {
                String: "String", Text: "Text",
                Integer: "Integer", Float: "Float",
                Boolean: "Boolean",
                # Add more mappings as needed (Date, DateTime, Enum, etc.)
            }
            # Find the closest match in the map
            for py_type, str_type in type_map.items():
                if isinstance(sqla_type, py_type):
                    return str_type
            return str(sqla_type.__class__.__name__) # Fallback

        # Iterate through the explicitly listed models
        model_classes = self.MODELS_FOR_SCHEMA
        model_labels = {model.__name__ for model in model_classes} # Get set of valid model names

        for model_cls in model_classes:
            try:
                mapper = object_mapper(model_cls()) # Get mapper for the class
                table = model_cls.__table__ # Get table object
                model_label = model_cls.__name__

                # --- Extract Node Info ---
                node_info = {
                    "label": model_label,
                    "primary_key": [pk_col.name for pk_col in mapper.primary_key], # List of PK column names
                    "properties": []
                }
                for column in table.columns:
                    node_info["properties"].append({
                        "name": column.name,
                        "type": map_type(column.type),
                        "nullable": column.nullable
                    })
                schema_nodes.append(node_info)

                # --- Extract Edge Info (from relationships) ---
                for rel_prop in mapper.relationships:
                    # Use a unique identifier for the relationship pair to avoid duplicates
                    rel_key = tuple(sorted((model_label, rel_prop.key)))
                    if rel_key in processed_relationships:
                        continue

                    target_cls_name = rel_prop.mapper.class_.__name__

                    # Ensure target is also a model we are processing
                    if target_cls_name not in model_labels:
                        continue

                    # Determine edge label (use relationship attribute name)
                    edge_label = rel_prop.key.upper()

                    # Determine direction (simplistic: from current model to related model)
                    source_label = model_label
                    target_label = target_cls_name

                    # Refine label for clarity if possible (e.g., HAS_GENOMES, BELONGS_TO_SAMPLE)
                    # This often requires manual naming conventions or more complex inference
                    if rel_prop.direction.name == 'MANYTOONE':
                        # e.g., Genome.sample -> GENOME_BELONGS_TO_SAMPLE (Genome -> Sample)
                        edge_label = f"{source_label.upper()}_BELONGS_TO_{target_label.upper()}"
                    elif rel_prop.direction.name == 'ONETOMANY':
                         # e.g., Sample.genomes -> SAMPLE_HAS_GENOMES (Sample -> Genome)
                         edge_label = f"{source_label.upper()}_HAS_{target_label.upper()}"
                    elif rel_prop.direction.name == 'MANYTOMANY':
                         # e.g., Protein.pfams -> PROTEIN_HAS_PFAM (Protein -> Pfam)
                         edge_label = f"{source_label.upper()}_HAS_{target_label.upper()}"
                    # Add more specific naming if desired

                    schema_edges.append({
                        "label": edge_label,
                        "source": source_label,
                        "target": target_label
                        # "secondary_table": rel_prop.secondary.name if rel_prop.secondary is not None else None # Optional M2M info
                    })
                    processed_relationships.add(rel_key) # Mark this relationship pair as processed

            except Exception as e:
                 print(f"Warning: Could not process model {model_cls.__name__} for schema: {e}")


        # Assemble the final schema dictionary
        schema_dict = {
            "format": format,
            "nodes": sorted(schema_nodes, key=lambda x: x['label']), # Sort for consistent output
            "edges": sorted(schema_edges, key=lambda x: (x['source'], x['target'])) # Sort for consistent output
        }

        # Convert to JSON string
        try:
            json_string = json.dumps(schema_dict, indent=4)
        except TypeError as e:
             print(f"Error serializing schema to JSON: {e}")
             return None # Indicate failure

        # Write to file or return string
        if path:
            try:
                with open(path, 'w') as f:
                    f.write(json_string)
                print(f"Schema successfully written to: {path}")
                return None # Indicate success writing to file
            except IOError as e:
                print(f"Error writing schema to file '{path}': {e}")
                raise # Re-raise IO error
        else:
            return json_string # Return the JSON string