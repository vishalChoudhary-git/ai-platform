# 07 — LLM Fundamentals — Interview Notes

## 1. LLM End-to-End Flow

At a high level:

```
Text
 ↓
Tokenization
 ↓
Token IDs + positional information
 ↓
Transformer layers
 ↓
Logits over vocabulary
 ↓
Decoding
 ↓
Next token
 ↓
Repeat until stop
```

During inference, the model generates tokens autoregressively for decoder-only LLMs.

## 2. Tokens and Tokenization

A token is a unit used by the model. It may represent a word, part of a word, punctuation, or other text fragment.

Tokenization converts text into token IDs from a fixed vocabulary.

Why it matters in production:

- Context windows are measured in tokens
- Input/output cost is token-dependent
- Long prompts increase latency and memory use

## 3. Vocabulary

The vocabulary is the finite set of token IDs the tokenizer can produce.

The model predicts probabilities over this vocabulary at each generation step.

## 4. Embeddings

An embedding maps a discrete token ID to a dense vector representation that the model can process.

Do not confuse **token embeddings** with **sentence/document embeddings** used for vector search. The latter are usually produced by a separate embedding model or a specialized model output.

## 5. Positional Information

Self-attention alone does not inherently encode token order, so transformer models need a mechanism to represent position.

Common approaches include learned positional embeddings and rotary positional embeddings (RoPE).

## 6. Transformer Architecture

### Encoder-Only

Builds contextual representations of input tokens.

Typical use: classification, embeddings, representation learning.

### Decoder-Only

Uses causal attention and predicts the next token.

Typical use: modern generative LLMs.

### Encoder-Decoder

Encoder processes the input; decoder generates the output while attending to the encoder representation.

Typical use: sequence-to-sequence tasks such as translation.

## 7. Self-Attention

Self-attention lets each token use information from other tokens in the same sequence.

Conceptually:

```
Q = what this token is looking for
K = what each token offers for matching
V = information to retrieve
```

The attention output is a weighted combination of value vectors.

## 8. Q, K and V

For hidden representation `X`, the model creates:

```
Q = XWq
K = XWk
V = XWv
```

The model uses Q and K to determine relevance, then uses those weights to combine V.

## 9. Attention Score, Scaling and Softmax

Scaled dot-product attention is commonly represented as:

```
Attention(Q,K,V) = softmax(QKᵀ / √dₖ)V
```

Scaling reduces the magnitude of dot products so softmax behaves more stably.

Softmax converts scores into normalized attention weights.

## 10. Multi-Head Attention

Instead of performing one attention operation, the model uses multiple heads.

Each head can learn different relationships or patterns, then the results are combined.

This gives the model multiple attention subspaces within the same layer.

## 11. Cross-Attention

Cross-attention lets one sequence attend to another sequence.

In encoder-decoder transformers, the decoder can use encoder representations through cross-attention.

It differs from self-attention because Q and K/V come from different sources.

## 12. Feed-Forward Network

After attention, transformer blocks typically apply a position-wise feed-forward network.

Its role is to perform nonlinear transformation of each token representation.

Conceptually:

```
Attention → Feed-forward → next block
```

## 13. Residual Connections

Residual connections add the block input back to the block output.

They improve optimization and help information and gradients flow through deep networks.

## 14. Layer Normalization

Layer normalization normalizes activations within a token representation dimension.

It helps stabilize training and is a standard component of transformer blocks.

## 15. Transformer Block

A simplified transformer block contains:

```
Input
 ↓
Normalization
 ↓
Attention
 ↓
Residual connection
 ↓
Normalization
 ↓
Feed-forward network
 ↓
Residual connection
```

Exact ordering varies by architecture.

## 16. Causal Attention

Causal attention prevents a token from attending to future tokens.

When generating token `t`, the model can only use tokens up to `t`.

This preserves autoregressive generation.

## 17. RoPE

RoPE (Rotary Positional Embeddings) incorporates position by rotating query/key representations according to token position.

A practical benefit is that positional relationships are encoded directly into attention interactions rather than simply adding a position vector.

## 18. KV Cache

During autoregressive generation, previous keys and values do not need to be recomputed for every new token.

The KV cache stores them for reuse.

**Benefit:** much lower repeated computation and generation latency.

**Trade-off:** KV cache consumes GPU memory and grows with sequence length and batch size.

## 19. Context Window

The context window is the maximum amount of token context the model can process for a request/generation setup.

Larger context can support longer documents and conversations, but does not automatically mean the model will use every part equally well.

Larger context also increases memory, latency, and often cost.

## 20. Mixture of Experts (MoE)

MoE models contain multiple expert networks, but each token is routed to only a subset of experts.

This can increase total model capacity without activating all parameters for every token.

Trade-off: routing and infrastructure are more complex.

## 21. Long-Context Models

Long-context models support very large input sequences.

The main production considerations are:

- Memory usage
- KV-cache size
- Latency
- Cost
- Retrieval quality
- Lost-in-the-middle behavior

Long context reduces the need for aggressive truncation, but it does not eliminate the need for retrieval and context management.

## 22. Multimodal Models

Multimodal models can process multiple modalities such as text, images, audio, or video.

The system converts modalities into representations that can be jointly processed or connected through the model architecture.

The engineering impact includes modality-specific preprocessing, token/compute cost, latency, and evaluation complexity.

## 23. Logits

Logits are the model's raw, unnormalized scores for the next token over the vocabulary.

Softmax converts logits into probabilities.

```
Logits → softmax → token probabilities → decoding
```

## 24. Temperature

Temperature changes the sharpness of the probability distribution.

- Lower temperature → more deterministic
- Higher temperature → more diverse/random

Temperature does not add intelligence; it changes sampling behavior.

## 25. Top-K Sampling

Top-K restricts sampling to the K most probable tokens before sampling.

A smaller K makes output more constrained.

## 26. Top-P Sampling

Top-P, or nucleus sampling, selects the smallest set of tokens whose cumulative probability reaches a threshold `P`, then samples from that set.

Unlike Top-K, the number of eligible tokens can vary dynamically.

## 27. Greedy Decoding

Greedy decoding always chooses the highest-probability next token.

**Pros:** deterministic and simple.

**Cons:** can produce repetitive or locally optimal outputs.

## 28. Beam Search

Beam search keeps multiple candidate sequences instead of only one.

It is common in some sequence-generation tasks but is less typical for open-ended chat generation where sampling is often preferred.

## 29. Sampling

Sampling chooses the next token probabilistically from the model distribution.

It can improve diversity but introduces variability.

## 30. Log Probabilities

Log probabilities express token probabilities on a logarithmic scale.

They are useful for analyzing model confidence, comparing candidate tokens, and some structured/classification workflows.

A high log probability does not guarantee that the generated claim is factually correct.

## 31. Why Context Length Affects Production Behavior

As context grows:

- More tokens must be processed
- Memory requirements increase
- Latency generally increases
- KV cache grows during generation
- Irrelevant context can reduce answer quality

Therefore, context management is a quality and systems problem, not only a model-limit problem.

## 32. Attention and Cost

A standard full self-attention operation has quadratic complexity with sequence length for the attention matrix, approximately `O(n²)` in sequence length.

This is one reason long-context inference is computationally expensive, although actual serving cost also depends on architecture and implementation.

## 33. Prompt Tokens vs Generated Tokens

There are two important inference phases:

### Prefill

The model processes the input prompt and builds the initial KV cache.

### Decode

The model generates output tokens one by one using the cached keys and values.

This distinction is important for latency and serving optimization.

## 34. Time to First Token vs Generation Throughput

**TTFT (Time to First Token):** time until the first generated token.

It is strongly affected by prompt length and prefill work.

**Decode throughput:** how quickly subsequent tokens are generated.

It is strongly affected by model size, hardware, KV cache, batching, and serving implementation.

## 35. Common Production Trade-offs

| Decision | Trade-off |
|---|---|
| Larger context | Better coverage vs more memory/latency/cost |
| Higher temperature | Diversity vs consistency |
| Larger model | Quality/capability vs cost/latency |
| Larger batch | Throughput vs per-request latency |
| KV cache | Faster decode vs higher memory usage |
| MoE | More capacity vs routing/system complexity |

## 36. Interview Mental Model

When explaining an LLM in an interview, use this sequence:

```
Text
→ tokenizer
→ token embeddings + position
→ transformer blocks
→ logits
→ decoding
→ next token
→ repeat
```

Then explain production behavior through:

```
context length + KV cache + batching + decoding + model size
```

## 37. Interview Questions

### Core

1. What happens when you send text to an LLM?
2. What is tokenization?
3. What is the model vocabulary?
4. Token embeddings vs document embeddings?
5. Why does a transformer need positional information?
6. Encoder-only vs decoder-only vs encoder-decoder?

### Attention / Transformer

7. Explain self-attention.
8. What are Q, K, and V?
9. Why do we divide by `√dₖ`?
10. What does softmax do in attention?
11. Why use multi-head attention?
12. Self-attention vs cross-attention?
13. What is the role of the feed-forward network?
14. Why are residual connections used?
15. Why is layer normalization used?
16. What is a transformer block?
17. What is causal attention?
18. What is RoPE?

### Inference

19. What is a KV cache?
20. Why does KV cache improve generation speed?
21. What is the downside of KV cache?
22. What is a context window?
23. Why does larger context increase latency and memory usage?
24. What are prefill and decode?
25. TTFT vs token generation throughput?

### Decoding

26. What are logits?
27. Temperature vs Top-K vs Top-P?
28. Greedy decoding vs sampling?
29. What is beam search?
30. When would you use deterministic decoding?
31. What are log probabilities useful for?

### Advanced

32. What is Mixture of Experts?
33. Why can MoE provide high capacity with sparse activation?
34. What are the challenges of long-context models?
35. Why does long context not automatically replace RAG?
36. What are multimodal models?
37. How does model size affect latency and cost?
38. Why is attention expensive for long sequences?