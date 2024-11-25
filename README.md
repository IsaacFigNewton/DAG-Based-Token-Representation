<h1>DAG-Based Tokenizer/Embedder</h1>

<br>
<br>

<h1>Encoding Approach Overview (Refactoring in progress)</h1>
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

<h2>Build DAG</h2>
See main design doc for process

<hr>

<h1>Future modifications</h1>
<p>Note: The following hasn't been implemented yet, but are some directions I might take the project.</p>
<h2>Convert the Suffix Tree</h2>
<ol>
  <li>Convert the 2D dict of tokens and their subtokens’ frequencies to a sparse tensor representing the corresponding counts of all tokens.</li>
  <li>Create a 2D diagonal tensor of all the tokens’ global frequencies, where (i, i) is the global occurrence count for token i.</li>
  <li>Take the reciprocal of all the entries along the diagonal.</li>
  <li>Multiply the 2D subtoken count tensor with the 2D global count tensor to get a new tensor representing the vector embeddings of all the tokens:
    <ul>
      <li>Each token’s embedding is a 1D vector representing the conditional probabilities of the resulting node, given its co-occurrence rate with all the other tokens.</li>
    </ul>
  </li>
</ol>

<h3>Create Transition Probability Tensor</h3>
<ol>
  <li>Create a new sparse N-D tensor to represent the transition probabilities between tokens, where N is the maximum context length.</li>
  <li>Using the token ⇒ token number map in conjunction with this new tensor and the suffix tree, run through the text again.</li>
  <li>Tokenize the text as you run through it again using the suffix tree, but this time from beginning to end instead of the other way around.</li>
  <li>Each time a new token is read:
    <ul>
      <li>For all m from 2 to N, where N is the maximum context length, store the occurrence rate of each series of m tokens in the entry defined so that the coordinate in each dimension corresponds to the mth token’s token number.</li>
      <li>Let the m=1 context slice just contain the global token frequencies along the diagonal.</li>
      <li>Create a new N-dim tensor to hold the transition probabilities.</li>
      <li>Once the N-dimensional context count tensor has been filled out, set each entry in the slices after the m=1 context slice to the current path’s frequency/(first token’s frequency x second token’s frequency) (like with WordPiece).</li>
    </ul>
  </li>
</ol>

<h2>More Directions:</h2>

<h3>Embedding:</h3>
<p>After this N-D context tensor has been created, let the vectorization of the entire text be represented with the N-1-D slice corresponding to the current context summed with reducing weighted slices ending with the current token before and after the current context, similar to backpropagation in a NN.</p>

<h3>Compression:</h3>
<p>Treat the token DAG as a Hopfield Network</p>
<p>Represent each token sequence based on the start of the path slice in the transition probabilities tensor. Let subsequent tokens after the first be predicted based on the likeliest sequence of token selections for arriving at the designated context level.</p>

<p><strong>Example:</strong> For a tensor with max context length=3 and 3 tokens, abc, d, e, and z:
  <br><code>Text	⇒ token #’s	⇒ ((starting token tensor indices in current slice), designated context level)</code>
  <br>Since <code>e</code> normally follows <code>abcd</code>, not <code>z</code>, you’d have to start at the slice involving that unlikely transition.
  <br><code>“abcdz” ⇒ (0, 1, 2)	⇒ (0 (using this to represent token tensor embedding for brevity), 1), (2, 0)</code>
</p>

<h1>Sauces</h1>
<ul>
  <li><a href="https://research.google/blog/a-fast-wordpiece-tokenization-system/">Wordpiece</a></li>
</ul>
