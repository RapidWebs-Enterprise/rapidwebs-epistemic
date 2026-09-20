# Research Report: Epistemic Enhancement for AI Agents

**Date:** 2026-09-20  
**Author:** Lucien (RapidWebs)  
**Scope:** State-of-the-art in LLM confidence, self-awareness, and error recovery

---

## Executive Summary

This research identifies critical capabilities missing from current Hermes/Honcho stack that would transform agents from "smart but fallible" to "reliable and self-improving." Based on 10+ papers from ACL 2025, NeurIPS 2025, ICLR 2025, and arXiv preprints.

**Key Finding:** Modern LLMs show emergent metacognitive abilities but lack **structured systems** to leverage them. Our plugin provides the missing infrastructure.

---

## Part 1: Confidence Estimation Research

### 1.1 Current State of the Art

**Evidence for Limited Metacognition in LLMs** (arXiv:2509.21545)
- Frontier LLMs (GPT-4, Claude 3.5) show rudimentary ability to assess their own confidence
- Tested via "Delegate Game": model can choose to answer or delegate based on uncertainty
- Token probabilities correlate with delegation decisions (up to 0.5 partial correlation)
- **Limitation:** Abilities are limited in resolution and context-dependent

**MUSE Framework** (Neural Networks 2025)
- Metacognition for Unknown Situations and Environments
- Two implementations: world-modeling + LLM-based
- Continuously learns competence assessment and uses it for strategy selection
- **Key Insight:** Self-assessment guides iterative cycles of strategy selection

**AutoMeco** (EMNLP 2025)
- Automated Meta-cognition Evaluation framework
- Uses perplexity as "lens" for meta-cognition
- MIRA strategy improves step-level scoring by 34%
- **Finding:** Models have intrinsic meta-cognition but need better evaluation

### 1.2 Implementation Implications

| Research Insight | Implementation |
|------------------|----------------|
| Token probability variance predicts correctness | Use confidence scoring based on token entropy |
| Uncertainty markers in text indicate low confidence | Pattern matching for "I'm not sure", "maybe" etc. |
| Tool usage increases reliability | Weight tool verification in confidence score |
| Response length correlates with certainty | Heuristic scoring based on response characteristics |

### 1.3 Proposed Confidence Model

```python
confidence = (
    0.25 * linguistic_certainty_score +      # Text pattern analysis
    0.30 * tool_verification_score +          # How many tools were used
    0.25 * consistency_score +                # Alignment with history
    0.20 * claim_verifiability_score          # Factual vs opinion
)
```

**Thresholds:**
- ≥ 0.8: High confidence — deliver without caveat
- 0.7-0.8: Moderate — suggest verification
- 0.5-0.7: Low — flag explicitly
- < 0.5: Very low — recommend user review

---

## Part 2: Self-Model Research

### 2.1 KnowSelf: Agentic Knowledgeable Self-Awareness (ACL 2025)

**Core Innovation:** Agents can selectively invoke knowledge based on situation awareness

**Three Thinking Modes:**
1. **Fast Thinking:** Agent knows the answer directly
2. **Slow Thinking:** Agent needs rethinking/reflection
3. **Knowledgeable Thinking:** Agent needs external knowledge

**Training Approach:**
- Two-stage: SFT + DPO (Direct Preference Optimization)
- Special tokens mark situation type
- Achieves superior performance with minimal knowledge use

**Key Insight for Us:**
- Self-awareness enables selective resource allocation
- Reduces unnecessary computation
- Improves planning efficiency

### 2.2 INWARD: Introspective Access to One's Own Behavior (NeurIPS 2025)

**Finding:** LLMs can access facts about themselves independent of training data

**Method:** Cross-prediction experiment
- M1 predicts M2's behavior on hypothetical scenarios
- M1 outperforms M2 predicting itself
- Evidence for privileged introspective access

**Implication:** Agents can maintain self-models that improve over time

### 2.3 MAGELLAN: Metacognitive Generalization of Learning Progress (NeurIPS 2025)

**Capability:** Agents learn to predict their own competence across goal spaces

**Method:**
- Leverage LLM's semantic understanding to cluster goals
- Estimate learning progress (LP) for unseen goals
- Enable sample-efficient curriculum learning

**Result:** Only method to fully master large evolving goal spaces

**Relevance:** Self-model should include competence estimation across task types

---

## Part 3: Hallucination Detection Research

### 3.1 HalMit: Progressive Generalization Bound Exploration (arXiv:2507.15903)

**Approach:** Black-box watchdog that models agent's generalization boundary

**Method:**
- Probabilistic fractal sampling to generate test queries
- Store query-response pairs in vector DB
- Compare new queries against boundary
- Flag responses near boundary as potential hallucinations

**Performance:** Outperforms existing approaches in multi-topic datasets

**Key Insight:** Per-agent generalization bounds are easier to identify than universal bounds

### 3.2 FACTCHECKMATE: Preemptive Hallucination Detection (EMNLP 2025)

**Innovation:** Detect hallucinations BEFORE generation using hidden states

**Results:**
- 70%+ preemptive detection accuracy
- 34.4% more factual outputs with intervention
- Works across Llama, Mistral, Qwen, Gemma families

**Mechanism:**
- Classifier predicts hallucination risk from input hidden states
- Intervention adjusts hidden states toward factual outputs
- Adds negligible inference overhead

### 3.3 HADEMIF: Dual-Space Hallucination Detection (ICLR 2025)

**Architecture:**
- **Output space:** Deep Dynamic Decision Tree (D3T) for prediction characteristics
- **Internal space:** MLP for token hidden states
- Combined calibration reduces ECE by 54%

**Key Finding:** Hallucinations manifest in BOTH output and internal spaces

---

## Part 4: Self-Reflection Research

### 4.1 Agent-R: Iterative Self-Training with Reflection (arXiv:2501.11425)

**Problem:** Agents can't recover from errors in interactive environments

**Solution:** Monte Carlo Tree Search (MCTS) for trajectory revision

**Method:**
1. Actor model identifies first error step
2. Splice with adjacent correct path from tree
3. Train on corrected trajectories
4. Iterate to improve error recovery

**Results:**
- +5.59% performance improvement
- Earlier error correction over iterations
- Prevents cascading errors and loops

### 4.2 SAMULE: Multi-Level Reflection Synthesis (EMNLP 2025)

**Three Reflection Levels:**
1. **Micro:** Single-trajectory error correction
2. **Meso:** Intra-task error taxonomy
3. **Macro:** Inter-task transferable insights

**Training:**
- Synthesize reflections across levels
- Fine-tune retrospective model via SFT
- Foresight-based reflection for interactive settings

**Benchmarks:** TravelPlanner, NATURAL PLAN, Tau-bench

### 4.3 DORA: Dynamic Optimization for Reflection (COLING 2025)

**Problem:** "Early Stop Reflection" — effective reflection only in early iterations

**Solution:** Dynamic prompt generation via small language model

**Method:**
- External SLM generates reflection prompts
- Bayesian Optimization tunes prompt generation
- Agent feedback drives adaptation

**Results:**
- +19% success in MiniWoB++
- +9% in Alfworld
- Mitigates early-stop pattern

---

## Part 5: Theory of Mind Research

### 5.1 ToM-SWE: User Mental Modeling for SWE Agents (2025)

**Architecture:** Dual-agent with dedicated ToM partner

**ToM Agent Capabilities:**
- Infers user goals, constraints, preferences
- Maintains persistent memory of user
- Provides suggestions to SWE agent

**Results:**
- 59.7% task success vs 18.1% baseline
- 86% utility rating in 3-week developer study

**Three-Tier Memory:**
1. Raw session storage
2. Session-based user model
3. Overall cross-session user model

### 5.2 M3: Mind Modeling Framework (SOCIALIZE 2025)

**Core Idea:** User modeling as mental-state attribution

**Framework:**
- Perception → Mentalisation → Action loop
- Explicit, revisable hypotheses about mental states
- Longitudinal continuity across interactions

**Key Distinction:**
- Traditional: Behavior → Direct adaptation
- Mind modeling: Behavior → Mental state hypothesis → Adaptation

### 5.3 Inverse Theory of Mind for Recommendation (arXiv:2608.11354)

**Pipeline:**
1. Reconstruct decision context from interactions
2. LLM-driven counterfactual reasoning
3. Multi-hypothesis abductive inference
4. Structured user persona synthesis

**Applications:** Next-action prediction, personality inference, held-out category prediction

---

## Part 6: Episodic Memory Research

### 6.1 Episodic Memory Position Paper (arXiv:2502.06975)

**Five Key Properties:**
1. Long-term storage
2. Explicit reasoning
3. Single-shot learning
4. Instance-specific content
5. Contextualized memories

**Research Questions:**
- RQ1: How to store in external memory?
- RQ2: How to segment into episodes?
- RQ3: How to retrieve relevant episodes?
- RQ4: How to handle partial observability?
- RQ5: How to consolidate into parameters?
- RQ6: What benchmarks are needed?

**Key Insight:** Complementary Learning Systems — fast episodic + slow semantic

### 6.2 EM-LLM: Human-Inspired Episodic Memory (ICLR 2025)

**Innovation:** Integrate episodic memory into LLMs without fine-tuning

**Method:**
- Bayesian surprise for event segmentation
- Graph-theoretic boundary refinement
- Two-stage retrieval: similarity + temporal contiguity

**Results:**
- Outperforms RAG on LongBench and ∞-Bench
- Retrieves across 10M tokens
- Surpasses full-context models on most tasks

### 6.3 AriGraph: Knowledge Graph + Episodic Memory (IJCAI 2025)

**Architecture:**
- Semantic memory: Knowledge graph triples
- Episodic memory: Edges connecting observations to triples

**Retrieval:**
- Semantic search for relevant triplets
- Episodic search for contextualized observations

**Environments:** Textworld, NetHack (text-based games)

---

## Part 7: Synthesis & Recommendations

### 7.1 What We Have vs. What We Need

| Capability | Current State | Gap | Research Support |
|------------|---------------|-----|------------------|
| Store conversations | ✅ LCM | — | — |
| Extract knowledge | ✅ Honcho KG | — | — |
| Schedule wake-ups | ✅ Consciousness | — | — |
| **Estimate confidence** | ❌ None | **Critical** | MUSE, AutoMeco |
| **Learn from mistakes** | ❌ None | **Critical** | KnowSelf, Agent-R |
| **Detect hallucinations** | ❌ None | **Critical** | HalMit, FACTCHECKMATE |
| **Model user mental states** | ⚠️ Partial | **Important** | ToM-SWE, M3 |
| **Temporal memory decay** | ⚠️ Partial | **Important** | Episodic Memory paper |
| **Self-reflection loops** | ❌ None | **Useful** | DORA, SAMULE |

### 7.2 Implementation Priority

**Phase 1 (P0 — Core Epistemic):**
1. Confidence estimation (2h)
2. Self-model persistence (4h)
3. Epistemic vigilance (6h)

**Phase 2 (P1 — Enhancement):**
4. Temporal decay (Honcho extension) (1h)
5. Context routing (LCM extension) (2h)
6. Basic ToM integration (Honcho extension) (4h)

**Phase 3 (P2 — Advanced):**
7. Multi-level reflection (DORA/SAMULE) (8h)
8. Episodic memory integration (4h)
9. Full cognitive architecture (16h)

### 7.3 Key Differentiators

**What no competitor has:**
- Epistemic awareness (confidence + vigilance)
- Persistent self-model across sessions
- Research-backed implementation (10+ papers)

**Competitive positioning:**
| Feature | OpenAI | LangChain | CrewAI | **Us** |
|---------|--------|-----------|--------|--------|
| Context management | ✅ | ✅ | ✅ | ✅ (LCM) |
| Knowledge graphs | ❌ | ❌ | ❌ | ✅ (Honcho) |
| Wake/scheduling | ❌ | ❌ | ❌ | ✅ (Consciousness) |
| **Confidence scoring** | ❌ | ❌ | ❌ | **✅** |
| **Self-model** | ❌ | ⚠️ | ❌ | **✅** |
| **Hallucination detection** | ❌ | ❌ | ❌ | **✅** |
| **Theory of Mind** | ❌ | ❌ | ❌ | **✅** |

---

## References

1. **MUSE** (2025) — "Metacognition for Unknown Situations and Environments"
2. **KnowSelf** (ACL 2025) — "Agentic Knowledgeable Self-Awareness"
3. **INWARD** (NeurIPS 2025) — "Introspective Access to One's Own Behavior"
4. **MAGELLAN** (NeurIPS 2025) — "Metacognitive Generalization of Learning Progress"
5. **HalMit** (2025) — "Progressive Generalization Bound Exploration"
6. **FACTCHECKMATE** (EMNLP 2025) — "Preemptive Hallucination Detection"
7. **HADEMIF** (ICLR 2025) — "Dual-Space Hallucination Detection"
8. **Agent-R** (2025) — "Iterative Self-Training with Reflection"
9. **SAMULE** (EMNLP 2025) — "Multi-Level Reflection Synthesis"
10. **DORA** (COLING 2025) — "Dynamic Optimization for Reflection"
11. **ToM-SWE** (2025) — "User Mental Modeling for SWE Agents"
12. **M3** (SOCIALIZE 2025) — "Mind Modeling Framework"
13. **Episodic Memory Position** (2025) — "Missing Piece for Long-Term LLM Agents"
14. **EM-LLM** (ICLR 2025) — "Human-Inspired Episodic Memory"
15. **AriGraph** (IJCAI 2025) — "Knowledge Graph + Episodic Memory"
