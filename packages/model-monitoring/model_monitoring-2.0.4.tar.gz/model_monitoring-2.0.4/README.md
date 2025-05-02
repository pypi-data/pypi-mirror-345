![Status](https://img.shields.io/badge/Status-Collaud-yellow)

# Repository model_monitoring
***
La repository contiene il codice per implementare il monitoring dei sistemi di ML in produzione con 8 classi:
1) **PerformancesMeasures** per computare le perfomances delle metriche
2) **PerfomancesDrift** per computare il drift delle performances tra dati corrrenti e dati storici e generare un sistema di alerting
3) **DataDrift** per computare il drift di dati tramite PSI (Population Stability Index) o test statistici (KS e Chi-Quadro) tra dati corrrenti e dati storici e generare un sistema di alerting 
4) **ReferenceMetaData** per computare un dizionario di metadati a partire da uno di riferimento
5) **FairnessMeasures** per computare le performances delle metriche di fairness
6) **FairnessDrift** per computare il drift delle performances di fairness tra dati corrrenti e dati storici e generare un sistema di alerting
7) **XAI** per computare la spiegabilità di un modello tramite lo scoring delle features nelle predizioni
8) **XAIDrift** per computare il drift nella spiegabilità del modello e generare un sistema di alerting

## Guida per sviluppatori

- _main_ branch ha una Policy che evita di inserire codice direttamente su di esso. Sono consentite solo Pull requests. Le Pull requests devono essere approvate da almeno 2 revisori, uno dei quali può essere il richiedente.
- Come best practice, il nome del ramo dovrebbe seguire questa convenzione di denominazione: **NNN-related_work_item** dove NNN è il numero assegnato da Azure all'elemento di lavoro correlato al ramo e related_work_item è il nome dell'elemento di lavoro sostituendo ' ' (spazi bianchi) con '_' (underscores). Tra il numero e il nome usa '-' (segno meno).
- Usa un virtual environment dedicato ([guarda le note](https://docs.google.com/document/d/163Rk4YRbDgbIJK-x3qfA78rGbGtvqMHGnqBD4iomNJU/edit) per il codice).
- Ricorda di riempire ed installare in modo opportuno i requirements.
```
pip install -r requirements.txt  --trusted-host artifactory.group.credem.net  -i https://artifactory.group.credem.net/artifactory/api/pypi/virtualPypi/simple
```
- Ricorda di intallare il pre-commit (solo per la prima volta)
```
pre-commit install
```
- Si noti che il pacchetto model_monitoring viene installato automaticamente installando i requirements. Se i requirements non vengono utilizzati, eseguire quanto segue per installare in editable mode:
```
pip install -e .
```

# Documentazione
(Visualizza la documentazione a questo [link](https://model-monitoring-lib.readthedocs.io/en/latest/)).

La documentazione del codice viene generata automaticamente utilizzando Sphinx in formato HTML.
I passaggi per generare la documetazione sono i seguenti:

1. Installa Sphinx presente nel file di `requirements.txt`:

```bash
pip install -r requirements.txt
```

2. Installa il codice come developer:
```bash
pip install -e .
```
3. Crea un folder `docs/` ed entra digitando da terminale:
```bash
cd docs/
```
4. Inizializza sphinx, se la prima volta, digitando da terminale:
```bash
sphinx-quickstart
```
Questo comando, dopo alcune domande, creerà una struttura del tipo:
```
source/          
|
└─── conf.py      
|
└─── index.rst
|
└─── _static/
|
└─── _templates/
build/    
Makefile
make.bat
```
Nel file `docs/source/conf.py`, puoi configurare Sphinx. Un esempio di `conf.py` può essere:
```python
import pathlib
import sys

sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix() + "/src/model_monitoring")
project = "Documentazione_Model_Monitoring"
copyright = "2025, Team AIS"
author = "Team AIS"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.napoleon"]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autosummary_generate = True
html_theme = "classic"
html_static_path = ["_static"]

```
Nei file `index.rst` e nei `_templates/` si può configurare l'autogenerazione della documentazione e i template da usare per farlo.

4. Builda la documentazione, digitando da terminale:
```bash
sphinx-build -b html source build
```
Il risultato sarà in `docs/build/index.html`.

## Struttura
```
model_monitoring/
|
└─── .pre-commit-config.yaml
|
└─── pyproject.toml
|
└─── LICENCE
|
└─── MANIFEST.in
|
└─── README.md
|
└─── requirements.txt
|
└─── setup.py
|
└─── .gitignore
|
└─── docs/
|   |── build/
|   |   └── (Generated HTML output will be here)
|   └── source/
|   |   ├── _static/
|   |   |   └── (Static files)
|   |   ├── _templates/
|   |   |   └── autosummary/
|   |   |       ├── class.rst
|   |   |       ├── base.rst
|   |   |       └── module.rst
|   |   ├── conf.py
|   |   ├── index.rst
|   |   └── modules/
|   |       └── (Autogenerated rst files will be here)
|   |
|   └── Makefile
|   |
|   └── make.bat
|
└─── src/
    |
    └─── model_monitoring/
        |
        └─── __init__.py
        |
        └─── additional_metrics.py
        |
        └─── config.py
        |
        └─── imputer.py
        |
        └─── utils.py
        |
        └─── config
        |       params.yml
        |       algorithm_settings.yml
        └─── model_performance
        |       __init__.py
        |       model_performance.py
        └─── perfomance_measures
        |       __init__.py
        |       performance_measures.py
        └─── data_drift
        |       __init__.py
        |       data_drift.py
        └─── reference_metadata
        |       __init__.py
        |       reference_metadata.py
        └─── fairness_measures
        |       __init__.py
        |       fairness_measures.py
        └─── fairness_drift
        |       __init__.py
        |       fairness_drift.py
        └─── XAI
        |       __init__.py
        |       xai.py
        └─── XAI_drift
        |       __init__.py
        |       XAI_drift.py
```
# Utilizzo
Settare i parametri di configurazione `algorithm_settings.yml` contenuto in `config/` per definire i parametri generali delle classi e il path di salvataggio dei reports. Settare i parametri di configurazione in `params.yml` contenuto in `config/` per cambiare i parametri di threshold di default. 
Una volta settati i parametri, si può lanciare un eventuale script python `main.py` che a seconda dei parametri di configurazione printerà gli Alert di Performances, Data Drift, Fairness e XAI se ve ne sono, e salva i report riassuntivi delle classi.