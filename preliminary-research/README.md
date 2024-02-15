# enclaveid-notebooks

Jupyter notebooks used for preliminary exploration in Colab / Runpod.

### mistral_intent_cost.ipynb
Ran Mistral on TGI to infer the intent behind a single search record. For example:

Q: `
Here is a recent google search: "bartosz milewski the earth is flat". What could this search be referring to? What is the intent of the user for this search?
`

A: `
It's possible that the user searching for "Bartosz Milewski the Earth is flat" is looking for information about Bartosz Milewski, a computer scientist and philosopher who has written extensively on topics related to artificial intelligence, programming languages, and philosophy. One of his notable works includes an essay titled "The Earth Is Flat," which argues against certain assumptions made by modern science and technology. It's important to note that while Milewski does have some controversial views, he is not known as a proponent of flat Earth theories. Therefore, the user's intent for this search may simply be to learn more about Milewski's ideas and opinions on various subjects, rather than seeking support for a particular belief system.
`

Anecdotally, even when considering the most ambiguous queries, the output is as good as GPT3.5 but at a fraction of the cost when batching (30x cheaper).

### bertopic_single_day.ipynb
### bertopic_multi_day.ipynb

Attempts at topic modeling with BERTopic at daily level and global level.

In order to provide a richer context to the embedding model and the c-TF-IDF step, I used the intent guesses by Mistral from the previous notebook. 

This apporach marginally improves the performance over using the raw search records, but it's still sub-par as more than 60% of the records remain unclassified.

Areas of further exploration would be:
- Tuning the parameters of HDBSCAN and UMAP
- Trying different grains of clustering (monthly, hourly, etc)
- Figuring out if all the unclassfied records aren't actually isolated

### mistral_seo_categories.ipynb

Another test with Mistral but for guessing SEO categories of intent (Informational/Transactional/Navigational/Commercial) as a potentially useful preprocessing step.

It might be useful to restrict the analysis to the Informational queries at the beginning as they provide data to infer more specific user traits.  

### gpt3_wikidata_test.ipynb

An attempt at Entity Linking (https://en.wikipedia.org/wiki/Entity_linking) using GPT3.5. 

Most entities returned by the model do not match the names in Wikidata and the entity IDs are made up.

Restricting the set of possible entities to describe the user's traits and experience provides a common interface for both building the application frontend and potentially allowing interaction between users in the future.
