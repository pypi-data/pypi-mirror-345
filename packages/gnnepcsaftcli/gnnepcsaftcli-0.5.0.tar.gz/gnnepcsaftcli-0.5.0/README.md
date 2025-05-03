# GNNePCSAFT CLI

Project focused in the use of graph neural networks to estimate the pure-component parameters of the Equation of State [ePC-SAFT](https://en.wikipedia.org/wiki/PC-SAFT).

The motivation of this work is to be able to use a robust Equation of State, ePC-SAFT, without prior need of experimental data. Equations of State are important to calculate thermodynamic properties, and are pre-requisite in process simulators.

Currently, the model takes in account only the hard-chain, dispersive and assoc terms of ePC-SAFT. Future work on polar and ionic terms are being studied.

Code is being developed mainly in Pytorch (PYG).

You can find the model deployed at [GNNePCSAFT Webapp](https://gnnepcsaft.wildsonbbl.com/).

A CLI to use the model can be found at [GNNePCSAFT CLI](https://github.com/wildsonbbl/gnnepcsaftcli) and installed with `pipx` or `uvx`:

```bash
pipx install gnnepcsaftcli
gnnepcsaftcli pred
```

```bash
uvx gnnepcsaftcli pred
```

## CLI

GNNePCsAFT CLI tool

**Usage**:

```console
gnnepcsaftcli [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--install-completion`: Install completion for the current shell.
- `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
- `--help`: Show this message and exit.

**Commands**:

- `pred`: Predict ePCSAFT parameters from SMILES...

## `pred`

Predict ePCSAFT parameters from SMILES with a GNNePCSAFT model

**Usage**:

```console
pred [OPTIONS]
```

**Options**:

- `--help`: Show this message and exit.
