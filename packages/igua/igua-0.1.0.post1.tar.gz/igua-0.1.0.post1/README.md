# 🦎 IGUA [![Stars](https://img.shields.io/github/stars/zellerlab/IGUA.svg?style=social&maxAge=3600&label=Star)](https://github.com/zellerlab/IGUA/stargazers)

*Iterative Gene clUster Analysis, a high-throughput method for gene cluster family identification.*

[![Actions](https://img.shields.io/github/actions/workflow/status/zellerlab/IGUA/test.yml?branch=main&logo=github&style=flat-square&maxAge=300)](https://github.com/zellerlab/IGUA/actions)
[![Coverage](https://img.shields.io/codecov/c/gh/zellerlab/IGUA?logo=codecov&style=flat-square&maxAge=3600)](https://codecov.io/gh/zellerlab/IGUA/)
[![PyPI](https://img.shields.io/pypi/v/igua.svg?logo=pypi&style=flat-square&maxAge=3600)](https://pypi.org/project/igua)
[![Bioconda](https://img.shields.io/conda/vn/bioconda/igua?logo=anaconda&style=flat-square&maxAge=3600)](https://anaconda.org/bioconda/igua)
[![AUR](https://img.shields.io/aur/version/python-igua?logo=archlinux&style=flat-square&maxAge=3600)](https://aur.archlinux.org/packages/python-igua)
[![Wheel](https://img.shields.io/pypi/wheel/igua.svg?style=flat-square&maxAge=3600)](https://pypi.org/project/igua/#files)
[![Python Versions](https://img.shields.io/pypi/pyversions/igua.svg?logo=python&style=flat-square&maxAge=3600)](https://pypi.org/project/igua/#files)
[![Python Implementations](https://img.shields.io/pypi/implementation/igua.svg?logo=python&style=flat-square&maxAge=3600&label=impl)](https://pypi.org/project/igua/#files)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-blue.svg?style=flat-square&maxAge=2678400)](https://choosealicense.com/licenses/gpl-3.0/)
[![Source](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=2678400&style=flat-square)](https://github.com/zellerlab/igua/)
[![Mirror](https://img.shields.io/badge/mirror-EMBL-009f4d?style=flat-square&maxAge=2678400)](https://git.embl.de/larralde/igua/)
[![GitHub issues](https://img.shields.io/github/issues/zellerlab/IGUA.svg?style=flat-square&maxAge=600)](https://github.com/zellerlab/IGUA/issues)
[![Docs](https://img.shields.io/readthedocs/igua/latest?style=flat-square&maxAge=600)](https://igua.readthedocs.io)
[![Changelog](https://img.shields.io/badge/keep%20a-changelog-8A0707.svg?maxAge=2678400&style=flat-square)](https://github.com/zellerlab/IGUA/blob/master/CHANGELOG.md)
[![Downloads](https://img.shields.io/pypi/dm/igua?style=flat-square&color=303f9f&maxAge=86400&label=downloads)](https://pepy.tech/project/igua)


## 🗺️ Overview

IGUA is a method for high-throughput content-agnostic identification of
Gene Cluster Families (GCFs) from gene clusters of genomic and metagenomic 
origin. It performs three clustering iteration to perform GCF assignment:

- *Fragment mapping identification*: Reduce the input sequence space by 
  identifying which gene clusters are fragments of each other. 
- *Nucleotide deduplication*: Find similar gene clusters in genomic space,
  using linear clustering with lower sequence identity and coverage.
- *Protein representation*: Compute a numerical representation of gene clusters
  in term of protein composition, using representatives from a protein sequence
  clustering, to identify more distant relatives not captured by the previous
  step.

Compared to similar methods such as [BiG-SLiCE](https://github.com/medema-group/bigslice) 
or [BiG-SCAPE](https://github.com/medema-group/BiG-SCAPE), IGUA does not use Pfam 
domains to represent gene cluster composition, using instead representatives
from an unsupervised clustering. This allows IGUA to accurately account for
proteins that may not be covered by Pfam, and avoids performing a costly annotation
step. The resulting protein representatives can be later annotated indepently
to transfer annotations to the GCFs.


## 🔧 Installing

IGUA can be downloaded directly from PyPI, which hosts pre-compiled 
distributions for Linux, MacOS and Windows. Simply install with `pip`:

```console
$ pip install igua
```

**Note that you will need to install MMseqs2 yourself through other means.**


## 💡 Running

### 📥 Inputs

The gene clusters to pass to IGUA must be in GenBank format, with gene 
annotations inside of `CDS` features. Several GenBank files can be passed
to the same pipeline run.

```console
$ igua -i clusters1.gbk -i clusters2.gbk ...
```

The GenBank locus identifier will be used as the name of each gene cluster. This
may cause problems with gene clusters obtained with some tools, such as antiSMASH.
If the input contains duplicate identifiers, the first gene cluster with a given 
identifier will be used, and a warning will be displayed.

### 📤 Outputs

The main output of IGUA is a TSV file which assigns a Gene Cluster Family to 
each gene cluster found in the input. The GCF identifiers are arbitrary, and
the prefix can be changed with the `--prefix` flag. The table will also record
the original file from which each record was obtained to facilitate resource
management. The table is written to the filename given with the `--output` 
flag.

The sequences of the representative proteins extracted from each cluster 
can be saved to a FASTA file with the `--features` flag. These proteins are
used for compositional representation of gene clusters, and can be used to
transfer annotations to the GCF representatives. The final compositional matrix 
for each GCF representative, which can be useful for computing distances 
between GCFs, can be saved as an `anndata` sparse matrix to a filename given 
with the `--compositions` flag.

### 📝 Workspace

MMseqs needs a fast scratch space to work with intermediate files while running
linear clustering. By default, this will use a temporary folder obtained with
`tempfile.TemporaryDirectory`, which typically lies inside `/tmp`. To use a 
different folder, use the `--workdir` flag.

### 🫧 Clustering

By default, IGUA will use **average** linkage clustering and a relative distance 
threshold of `0.8`, which corresponds to clusters inside a GCF having at most
20% of estimated difference at the amino-acid level. These two options can be
changed with the `--clustering-method` and `--clustering-distance` flags.

Additionally, the precision of the distance matrix used for the clustering can
be lowered to reduce memory usage, using `single` or `half` precision floating
point numbers instead of the `double` precision used by default. Use the
`--precision` flag to control numerical precision.


## 💭 Feedback

### ⚠️ Issue Tracker

Found a bug ? Have an enhancement request ? Head over to the [GitHub issue
tracker](https://github.com/zellerlab/IGUA/issues) if you need to report
or ask something. If you are filing in on a bug, please include as much
information as you can about the issue, and try to recreate the same bug
in a simple, easily reproducible situation.

### 🏗️ Contributing

Contributions are more than welcome! See
[`CONTRIBUTING.md`](https://github.com/zellerlab/IGUA/blob/main/CONTRIBUTING.md)
for more details.


## 📋 Changelog

This project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)
and provides a [changelog](https://github.com/zellerlab/IGUA/blob/main/CHANGELOG.md)
in the [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) format.


## ⚖️ License

This library is provided under the [GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/).

*This project was developed by [Martin Larralde](https://github.com/althonos/) 
during his PhD project at the [European Molecular Biology Laboratory](https://www.embl.de/) 
and the [Leiden University Medical Center](https://lumc.nl/en/)
in the [Zeller team](https://github.com/zellerlab).*
