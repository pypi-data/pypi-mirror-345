"""GNNePCsAFT CLI tool"""

from pathlib import Path

import typer
from gnnepcsaft_mcp_server.utils import predict_epcsaft_parameters
from rich import print as richprint
from rich.prompt import Prompt

# lazy loads
# import numpy as np
# import onnxruntime as ort

# from gnnepcsaft.data.ogb_utils import smiles2graph
# from gnnepcsaft.data.rdkit_util import assoc_number, smilestoinchi

app = typer.Typer()

file_dir = Path(__file__)


@app.callback()
def callback():
    """
    GNNePCsAFT CLI tool
    """


@app.command()
def pred():
    """
    Predict ePCSAFT parameters from SMILES with a GNNePCSAFT model
    """

    while True:
        try:
            smiles = Prompt.ask(
                "\nEnter a valid[green] SMILES [/green]or [yellow]/bye[/yellow] to exit",
            )
            if smiles == "/bye":
                richprint("\n[green] :rocket:  Bye! :rocket: [/green]")
                break
            richprint(
                f"\n:star2::test_tube::thermometer: "
                f"[yellow]Predicting parameters for SMILES:[/yellow] "
                f"[green]{smiles}[/green] "
                f":star2::test_tube::thermometer:\n"
            )
        except KeyboardInterrupt:
            richprint("\n[green] :rocket:  Bye! :rocket: [/green]")
            break

        try:
            para = [round(p, 5) for p in predict_epcsaft_parameters(smiles)]
            msigmae = para[:3]
            assoc = para[3:5]
            na = para[6]
            nb = para[7]
            richprint("[ m sigma e ]: " + str(msigmae))
            richprint("[ k_ab e_ab ]: " + str(assoc))
            richprint(f"[  na, nb   ]: [  {na}, {nb}  ]")
        except (RuntimeError, ValueError, TypeError):
            richprint(
                "[red]Error[/red]: [yellow]SMILES[/yellow] not valid, "
                "please enter a valid [yellow]SMILES[/yellow]"
            )
