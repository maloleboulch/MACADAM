class Taxonomy:
    def __init__(self, id, name, type_of_name, parent_tax_id, taxonomic_rank, taxonomy):
        self.id = id
        self.name = name
        self.type_of_name = type_of_name
        self.parent_tax_id = parent_tax_id
        self.taxonomic_rank = taxonomic_rank
        self.taxonomy = taxonomy

    def __str__(self) -> str:
        return 'Taxonomy(id=' + str(self.id) + ', name=' + self.name + ', type_of_name=' + self.type_of_name + \
               ', parent_tax_id=' + str(self.parent_tax_id) + ', taxonomic_rank=' + self.taxonomic_rank + \
               ', taxonomy=' + self.taxonomy + ')'

    def __repr__(self) -> str:
        return str(self)
