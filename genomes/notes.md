short files:

### 23andme - columns
'# rsid', 'chromosome', 'position', 'genotype

### llumina - columns
'Chromosome', 'Position', 'Allele Frequency', 'Gene', 'Transcript',
'DNA Change', 'Amino Acid Change', 'Allele State', 'dbSNPID',
'Classification_1', 'Associated Condition_1', 'Inheritance Mode_1',
'PMIDs_1', 'Classification_2', 'Associated Condition_2',
'Inheritance Mode_2'
       
#### matching
chromosome 
position
dbSNPID/# rsid - some dbSNPID are null (5308 have values out of 5375)
what to do about genotype and Gene?
do we create the embeddings from these columns or a subset?
