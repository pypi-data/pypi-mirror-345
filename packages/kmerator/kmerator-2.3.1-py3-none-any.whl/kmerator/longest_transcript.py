### Not used
### Not finished

def longest_transcript(args, gene_name, transcriptome_dict):
    if args.verbose: print(f"{'-'*9}\n{Color.YELLOW}Finding the longest variant for the gene {gene_name}.{Color.END}")
    transcripts_dict = { k:len(v) for (k,v) in transcriptome_dict.items() if k.startswith(f"{gene_name}:")}
    # ~ print(*[k for k in variants_dict], sep='\n')
    nb_transcripts = len(transcript_dict)
    if args.verbose: print(f"{Color.YELLOW}Number of variants: {nb_transcripts}")
    longest_transcript = None
    length = 0
    for k,v in transcript_dict.items():
        if v > length:
            length = v
            longest_transcript = ':'.join(k.split(':')[1:2])
    # ~ print(f"{longest_variant = }")
    return longest_transcript
