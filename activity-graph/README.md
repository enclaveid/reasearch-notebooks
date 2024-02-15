# Algo

- summarize all raw data chunks: description, topics array
- get embeddings for all descriptions + topics arrays
- (opt) deduplicate embeddings if too close semantically and in time 
- initialize activity graph with broad interest categories taxonomy, and get embeddings
- for each summary get closest embedding, with T < curr
- summarize each subtree at the end, tag with life-event (yn)
