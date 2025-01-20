<h1>DAG-Based Tokenizer</h1>

<br>
<br>

<h1>Encoding Approach Overview</h1>
<h2>TODO: Update the readme with the current design</h2>

<h2>Create Storage Objects:</h2>
  
<ul>
  <li><strong>Create dictionaries for:</strong>
    <ul>
      <li>Tokens mapping them to their token numbers</li>
      <li>Token numbers that map to dictionaries of all token numbers that map to token frequencies (for tracking frequency of current node relative to its composing nodes)</li>
      <li>Tokens that map to their frequencies</li>
    </ul>
  </li>
  <li><strong>Instantiate ordered lists for:</strong>
    <ul>
      <li>Tokens (their positions in the list represent their token numbers)</li>
      <li>Edges (originating token number, destination token number)</li>
    </ul>
  </li>
</ul>


<h2>Build a Modified Suffix Tree</h2>

<ol>
  <li>Start with an alphabet of 1-grams for the first layer.</li>
  <li>Reset the suffix parsing process at the end of every clause, doc, etc.</li>
  <li>Build on the previous suffix tree.</li>
  <li>For each new suffix read:
    <ul>
      <li>Update the counts for all component nodes/tokens as the suffix path is traversed in the:
        <ul>
          <li>Dictionary of token obje</li>
          <li>Token frequencies dict</li>
        </ul>
      </li>
      <li>If it leads to a new node or an edge split, add new entries to:
        <ul>
          <li>Token list</li>
          <li>Edge list</li>
          <li>Token: number mapping dictionary</li>
          <li>2D dictionary</li>
          <li>Token frequencies dict</li>
        </ul>
      </li>
    </ul>
  </li>
</ol>

<h2>Directions for Future Work</h2>
<ul>
  <li>Add token composition likelihoods
    <ul>
      <li>Likely leads to some kind of Boltzmann machine</li>
    </ul>
  </li>
  <li>Replace base set of primitive tokens with word tokens and their POS tags
    <ul>
      <li>Create PCFG by modelling POS tag/word pair composition likelihoods</li>
    </ul>
  </li>
</ul>

<h1>Sauces</h1>
<ul>
  <li><a href="https://research.google/blog/a-fast-wordpiece-tokenization-system/">Wordpiece</a></li>
</ul>
