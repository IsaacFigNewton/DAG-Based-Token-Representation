<h1>SuffixNode Class</h1>
Let:

<ul>
<li>n=text length</li>
<li>b=mean block size</li>
<li>l=mean inter-block lexical diversity (l = n/b if every block has a unique suffix tree and l < n/b if some blocks have shared suffix tree compositions)</li>
</ul>

Blocked Ukkonen time complexity: O(n)
<ul>
<li>If split with preprocessing (O(n) time), parallelization in a divide-and-conquer approach would offer maximum time complexity of O(b*l)</li>
</ul>

pruning time complexity: O(log(b*l))
tokenization time complexity: O(log(b*l))