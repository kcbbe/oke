# Relevant snip of kept experiment log

## 27 October 25 (Start with putting everything together..)
Started experiments with name: 251013_pest_PD
Used search terms: "(pesticide OR pesticides) AND parkinson's"

Run with complete `main_part1.sh`

```
Busy with experiment: free_1000_251013_pest_PD
See log file for progress: logs/251013_pest_PD.log
Experiment free_1000_251013_pest_PD finished.
NOTE: Run 'corpus2vectors.sh' to get the embedding and similarity scores.
```
See log file `logs/251013_pest_PD_part1a.log`

Something went wrong at meta2pdf: argparse missed an argument that was flagged as required.
Fixed error and rerun experiment starting with meta2pdf.
See log file `logs/251013_pest_PD_part1b.log`

A Sankey diagram has been made with the pmid_dropouts.ipynb.
See `explorations/img/pmid_dropout_251013_pest_PD.png`

It took ~ 3 minutes to run `main_part1.sh`
(Note: most papers were already downloaded/parsed)

[[
    part1a
    start: ma 27 okt 2025 17:24:43 CET
    end: ma 27 okt 2025 17:26:37 CET

    part1b
    start: ma 27 okt 2025 17:43:26 CET
    end: ma 27 okt 2025 17:44:17 CET
]]

## 3 November 25
Continued with previous experiment: `251013_pest_PD`

Run with complete `main_part2.sh`

```
Busy with experiment: free_1000_251013_pest_PD
See log file for progress: logs/251013_pest_PD_corpus_by_sentence2vector_a25.log
Experiment is finished.
```

It took ~ 2.5 minutes to run `main_part2.sh`.

[[
	start: ma  3 nov 2025 12:29:02 CET
	end: ma  3 nov 2025 12:31:33 CET
]]

## 7 November 25
Started experiments with name: `251107_PFAS_cancer`
Used search terms: "(PFAS OR teflon OR PFOS OR PFOA) AND cancer"
Terminal: `bash main_part1.sh && sbatch main_part2.sh`

```
Busy with experiment: free_1000_251107_PFAS_cancer
See log file for progress: logs/251107_PFAS_cancer.log
Experiment free_1000_251107_PFAS_cancer has finished.
NOTE: Run 'sbatch main_part2.sh' to get the vector embeddings, similarity scores, and a networkx graph.
Submitted batch job 5329
```

It took ~ 6 minutes to run `main_part1.sh` (incl. downloading (61 papers) and parsing (54 success))

[[
	start: vr  7 nov 2025 11:09:06 CET
	end: vr  7 nov 2025 11:15:06 CET
]]

Part `main_part2.sh` is currently in queue. 

## Update on 10 Nov '25
It finished!
It took ~ 2.5 minutes to run `main_part2.sh`.

[[
	start: zo  9 nov 2025 19:46:37 CET
	end: zo  9 nov 2025 19:48:05 CET
]]

## 12 December '25
Noticed that `meta_free_1000_251013_pest_PD.csv` has incorrect values for `is_accepted` and `is_published`.. Other testing runs done before and after this run appear oke.
Renamed original file `meta_free_1000_251013_pest_PD_artifacts.csv`
Re-run of `pmid2meta.py` with debugger to check process. No log files were created.
