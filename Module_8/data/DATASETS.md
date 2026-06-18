# Module 8 — Datasets

## Logistics supply chain (warehouse / inventory lab)

| File | Rows | Use case |
|------|------|----------|
| `logistics-supply-chain/dynamic_supply_chain_logistics_dataset.csv` | 32,065 | **`Module_8_Exploring_Logistics_and_Supply_Chain_Dataset.ipynb`** — beginner EDA & field guide |
| | | **`Module_8_Warehouse_Inventory_Management_with_Knowledge_Graphs.ipynb`** — weekly warehouse inventory KG |

- Source: [Kaggle — Logistics and supply chain dataset](https://www.kaggle.com/datasets/datasetengineer/logistics-and-supply-chain-dataset) (CC0-1.0)
- Download with Kaggle CLI:

```bash
kaggle datasets download -d datasetengineer/logistics-and-supply-chain-dataset \
  -p Module_8/data/logistics-supply-chain --unzip
```

## Recommended for the notebook

| File | Entries | Size | Use case |
|------|---------|------|----------|
| **`dbpedia_course_corpus.txt`** | 100 | ~100 KB | **Default** — rich unstructured text for LLM graph extraction |
| `dbpedia_maritime_corpus.txt` | 37 | ~15 KB | Maritime/logistics theme (faster runs, domain-focused schema) |
| `dbpedia_abstracts_sample.txt` | 7 | ~2 KB | Legacy tiny demo (not recommended for full labs) |

## Source (open data)

### Primary: DBpedia Summarizer sample (100 English articles)

- Repository: [dice-group/DBpedia-Summarizer](https://github.com/dice-group/DBpedia-Summarizer)
- File: `data_eval/en_100_summaries.csv`
- License: DBpedia / Wikipedia (**CC BY-SA**)
- Download:

```bash
curl -fsSL -o Module_8/data/dbpedia_en_100_summaries.csv \
  https://raw.githubusercontent.com/dice-group/DBpedia-Summarizer/master/data_eval/en_100_summaries.csv
```

Rebuild text corpora:

```bash
python Module_8/scripts/build_dbpedia_corpus.py
```

### Optional: larger maritime subset (SPARQL)

When you have internet access, download more port/shipping-related abstracts:

```bash
python Module_8/scripts/download_dbpedia_maritime_sparql.py --limit 150
```

Output: `data/dbpedia_maritime_sparql.txt`

Then set in the notebook:

```python
SAMPLE_TEXT_PATH = MODULE_DIR / "data" / "dbpedia_maritime_sparql.txt"
```

## Switching dataset in the notebook

In **Step 0b**, change:

```python
# Default (100 articles)
SAMPLE_TEXT_PATH = MODULE_DIR / "data" / "dbpedia_course_corpus.txt"

# Maritime-focused (smaller, faster)
# SAMPLE_TEXT_PATH = MODULE_DIR / "data" / "dbpedia_maritime_corpus.txt"
```

## References for teaching

- [DBpedia](https://www.dbpedia.org/) — open knowledge graph from Wikipedia
- [Neo4j — Creating KG from unstructured data](https://neo4j.com/developer/genai-ecosystem/importing-graph-from-unstructured-data/)
