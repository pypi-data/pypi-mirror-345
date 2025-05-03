from typing import Optional, List


class RefSeqTranscript:
    def __init__(self, mrna: str, protein: str):
        self.mrna = mrna
        self.protein = protein

    def __repr__(self):
        return f"RefSeqTranscript(mRNA='{self.mrna}', protein='{self.protein}')"


class Gene:
    def __init__(
        self,
        symbol: str,
        name: str,
        chromosome: str,
        band: str,
        primary_transcript: RefSeqTranscript,
        secondary_transcript: Optional[RefSeqTranscript] = None
    ):
        self.symbol = symbol
        self.name = name
        self.chromosome = chromosome
        self.band = band
        self.primary_transcript = primary_transcript
        self.secondary_transcript = secondary_transcript

    def __repr__(self):
        return (
            f"Gene(symbol='{self.symbol}', name='{self.name}', "
            f"chromosome='{self.chromosome}', band='{self.band}', "
            f"primary_transcript={self.primary_transcript}, "
            f"secondary_transcript={self.secondary_transcript})"
        )


class GeneRegistry:
    def __init__(self, genes: List[Gene]):
        self.genes = genes
        self.by_symbol = {gene.symbol: gene for gene in genes}
        self.by_primary_mrna = {
            gene.primary_transcript.mrna: gene for gene in genes
        }

    def get_gene(self, symbol: str) -> Optional[Gene]:
        return self.by_symbol.get(symbol)

    def get_secondary_transcript(self, primary_mrna: str) -> Optional[RefSeqTranscript]:
        gene = self.by_primary_mrna.get(primary_mrna)
        return gene.secondary_transcript if gene else None


# Static data definition
GENES = [
    Gene(
        symbol="FOXG1",
        name="forkhead box G1",
        chromosome="14",
        band="14q12",
        primary_transcript=RefSeqTranscript("NM_005249.5", "NP_005240.3")
    ),
    Gene(
        symbol="MECP2",
        name="methyl-CpG binding protein 2",
        chromosome="X",
        band="Xq28",
        primary_transcript=RefSeqTranscript("NM_004992.4", "NP_004983.1"),
        secondary_transcript=RefSeqTranscript("NM_001110792.2", "NP_001104262.1")
    )
]


# Registry instance for use at runtime
registry = GeneRegistry(GENES)
