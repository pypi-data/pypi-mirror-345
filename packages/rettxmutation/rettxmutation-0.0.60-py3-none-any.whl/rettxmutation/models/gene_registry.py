from typing import Optional, List
from pydantic import BaseModel, AnyUrl, Field


class RefSeqTranscript(BaseModel):
    mrna: str = Field(..., description="RefSeq mRNA ID, e.g., NM_004992.4")
    protein: str = Field(..., description="RefSeq protein ID, e.g., NP_004983.1")


class Gene(BaseModel):
    symbol: str = Field(..., description="Gene symbol, e.g., MECP2")
    name: str = Field(..., description="Gene name, e.g., methyl-CpG binding protein 2")
    chromosome: str = Field(..., description="Chromosome number, e.g., X")
    band: str = Field(..., description="Cytogenetic band, e.g., Xq28")
    primary_transcript: RefSeqTranscript = Field(..., description="Primary transcript information")
    secondary_transcript: Optional[RefSeqTranscript] = Field(None, description="Secondary transcript information (if available)")
    ncbi_gene_id: AnyUrl = Field(..., description="NCBI Gene ID")
    omim_id: AnyUrl = Field(..., description="OMIM ID")


class GeneRegistry:
    def __init__(self, genes: List[Gene]):
        self.genes = genes
        self.by_symbol = {g.symbol: g for g in genes}
        self.by_primary_mrna = {g.primary_transcript.mrna: g for g in genes}

    def get_gene(self, symbol: str) -> Optional[Gene]:
        return self.by_symbol.get(symbol)

    def get_secondary_transcript(self, primary_mrna: str) -> Optional[RefSeqTranscript]:
        gene = self.by_primary_mrna.get(primary_mrna)
        return gene.secondary_transcript if gene else None


# Static data definition —
GENES: List[Gene] = [
    Gene(
        symbol="MECP2",
        name="methyl-CpG binding protein 2",
        chromosome="X",
        band="Xq28",
        primary_transcript=RefSeqTranscript("NM_004992.4", "NP_004983.1"),
        secondary_transcript=RefSeqTranscript("NM_001110792.2", "NP_001104262.1"),
        ncbi_gene_id="https://www.ncbi.nlm.nih.gov/gene/4204",
        omim_id="https://omim.org/entry/300005",
    ),
    Gene(
        symbol="FOXG1",
        name="forkhead box G1",
        chromosome="14",
        band="14q12",
        primary_transcript=RefSeqTranscript("NM_005249.5", "NP_005240.3"),
        secondary_transcript=None,
        ncbi_gene_id="https://www.ncbi.nlm.nih.gov/gene/2290",
        omim_id="https://omim.org/entry/164874",
    ),
    Gene(
        symbol="SLC6A1",
        name="solute carrier family 6 member 1",
        chromosome="3",
        band="3p25.3",
        primary_transcript=RefSeqTranscript("NM_003042.4", "NP_003033.3"),
        secondary_transcript=None,
        ncbi_gene_id="https://www.ncbi.nlm.nih.gov/gene/6529",
        omim_id="https://omim.org/entry/137165",
    ),
]

# Registry instance for runtime lookup
registry = GeneRegistry(GENES)
