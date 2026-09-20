# Research Report: Hallucination Detection & Mitigation

**Date:** 2026-09-20  
**Author:** Lucien (RapidWebs)  
**Focus:** State-of-the-art in hallucination detection for LLM agents

---

## Executive Summary

Hallucinations are the #1 reliability concern for production AI agents. This report analyzes 5 cutting-edge approaches to hallucination detection and mitigation, with recommendations for implementation in the rapidwebs-epistemic plugin.

**Key Finding:** Best results come from combining **preemptive detection** (before generation) with **post-hoc verification** (after generation).

---

## 1. HalMit: Black-Box Watchdog Framework

**Source:** arXiv:2507.15903

### Problem
Existing methods require white-box access to LLM internals or fail to accurately identify hallucinations in black-box commercial models.

### Solution
Models agent's **generalization boundary** — the space of valid query-response pairs. Responses outside this boundary are flagged as hallucinations.

### Method
1. **Multi-agent bound exploration:** Generate parallel queries to map boundary
2. **Probabilistic fractal sampling:** Efficiently cover boundary space
3. **Vector DB storage:** Store query-response pairs with context
4. **Cosine similarity comparison:** Flag queries near boundary

### Results
- Significantly outperforms existing approaches
- Works across multi-topic datasets
- Black-box compatible (no internal model access needed)

### Implementation Considerations
- Requires vector DB (Honcho already has this)
- Boundary exploration can be done during idle time
- Real-time comparison is lightweight

---

## 2. FACTCHECKMATE: Preemptive Detection

**Source:** EMNLP 2025

### Innovation
Predicts hallucinations **BEFORE** generation using hidden states

### Method
1. **Classifier on hidden states:** Learns to predict hallucination risk from input-conditioned hidden states
2. **Intervention:** Adjusts hidden states toward "factual target state"
3. **Lightweight:** Adds <2% parameters relative to base model

### Results
- 70%+ preemptive detection accuracy
- 34.4% more factual outputs with intervention
- Consistent across Llama, Mistral, Qwen, Gemma families

### Implementation Considerations
- Requires access to model hidden states (not available in black-box)
- Can use proxy metrics: token probability variance, entropy
- Intervention requires model modifications (not feasible for hosted APIs)

---

## 3. HADEMIF: Dual-Space Detection

**Source:** ICLR 2025

### Architecture
Combines **output space** and **internal space** detection:

1. **Output space:** Deep Dynamic Decision Tree (D3T) using prediction characteristics
   - Inputs: confidence, uncertainty, consistency
   - Output: hallucination classification

2. **Internal space:** MLP using token hidden states
   - Captures deep semantic hallucinations
   - Learns mapping from hidden states to hallucination indicators

### Calibration
Uses detection outputs to calibrate predictions:
- Maximizes token probabilities for correct generations
- Reduces likelihood of incorrect ones

### Results
- 5% improvement in accuracy@50
- 54% reduction in Expected Calibration Error (ECE)
- 18% reduction in Brier score

### Implementation Considerations
- D3T can be trained offline on historical data
- MLP requires hidden state access (same limitation as FACTCHECKMATE)
- Calibration can be approximated with confidence weighting

---

## 4. InEx: Introspection + Multi-Agent Collaboration

**Source:** AAAI 2025

### Cognitive Paradigm
Mirrors human decision-making:
1. **Introspection:** Reduce uncertainty via internal reasoning
2. **External collaboration:** Verify through diverse perspectives

### Method
1. **Internal reasoning:** Entropy-based uncertainty estimation
2. **Cross-modal collaboration:** Multiple agents verify from different angles
3. **Iterative refinement:** Alternate between verification and reflection

### Key Metric: Text-to-Visual Entropy Ratio (TVER)
- Most effective for detecting hallucination patterns
- Measures divergence between modalities

### Results
- 4-27% gains on hallucination benchmarks
- Strong robustness across modalities

### Implementation Considerations
- Requires multi-agent setup (we have subagent infrastructure)
- Can adapt for single-agent with simulated collaboration
- Entropy estimation available from LLM outputs

---

## 5. GUARDIAN: Temporal Graph Modeling

**Source:** NeurIPS 2025

### Problem
Multi-agent collaboration faces hallucination amplification and error propagation

### Solution
Models collaboration as **temporal attributed graph**:
- Nodes: agents at different timesteps
- Edges: inter-agent communications
- Attributes: agent responses

### Architecture
1. **Attributed Graph Encoder:** Captures structural + attribute correlations
2. **Time Information Encoder:** Integrates historical patterns
3. **Attribute Reconstruction Decoder:** Detects node-level anomalies
4. **Structure Reconstruction Decoder:** Detects edge-level anomalies

### Graph Abstraction
Uses Information Bottleneck Theory to compress temporal graphs while preserving essential patterns

### Results
- 80%+ anomaly detection rate
- Peak 94.74% accuracy
- Low false discovery rate (<20%)

### Implementation Considerations
- Graph construction overhead
- Best suited for multi-agent scenarios
- Can be adapted for single-agent with session history graph

---

## Comparative Analysis

| Method | Detection Type | Access Required | Latency | Accuracy | Complexity |
|--------|---------------|-----------------|---------|----------|------------|
| HalMit | Post-hoc | None (black-box) | Medium | High | Medium |
| FACTCHECKMATE | Preemptive | Hidden states | Low | 70%+ | High |
| HADEMIF | Hybrid | Hidden states | Low | Highest | High |
| InEx | Multi-agent | None | High | High | Medium |
| GUARDIAN | Temporal graph | None | High | High | Very High |

---

## Recommendations for rapidwebs-epistemic

### Phase 1: Lightweight Detection (No Hidden State Access)
```python
class LightweightVigilance:
    """
    Implements HallMit-inspired detection without internal model access.
    Uses output characteristics + historical boundary.
    """
    
    def detect_hallucination(self, query, response, context=None):
        # 1. Check for uncertainty markers
        uncertainty = self._count_uncertainty_markers(response)
        
        # 2. Verify against historical boundary
        similar_queries = self._retrieve_similar_queries(query)
        consistency = self._check_consistency(similar_queries, response)
        
        # 3. Check claim verifiability
        claims = self._extract_claims(response)
        verifiable = sum(1 for c in claims if self._has_source(c))
        
        # Combined score
        return {
            "hallucination_risk": max(0, uncertainty - consistency - verifiable),
            "factors": {
                "uncertainty": uncertainty,
                "consistency": consistency,
                "verifiability": verifiable
            }
        }
```

### Phase 2: Advanced Detection (With Honcho Integration)
```python
class AdvancedVigilance:
    """
    Implements HALMit-style boundary checking using Honcho KG.
    """
    
    def __init__(self, honcho_client):
        self.honcho = honcho_client
        self.boundary_db = VectorDB()  # Query-response pairs
    
    def check_against_boundary(self, query, response):
        # Retrieve similar historical queries
        similar = self.boundary_db.search(query, k=5)
        
        # Check if response is within learned boundary
        boundary_score = self._compute_boundary_deviation(similar, response)
        
        return boundary_score < THRESHOLD  # Below threshold = suspicious
```

### Phase 3: Multi-Agent Verification (Future)
```python
class MultiAgentVerification:
    """
    Implements InEx-style cross-agent verification.
    """
    
    def verify_response(self, query, response):
        # Spawn verification agents
        verifier_1 = self._spawn_agent("fact_checker")
        verifier_2 = self._spawn_agent("logic_checker")
        verifier_3 = self._spawn_agent("source_checker")
        
        # Collect verdicts
        verdicts = await asyncio.gather(
            verifier_1.check(response),
            verifier_2.check(response),
            verifier_3.check(response),
        )
        
        # Consensus mechanism
        return self._consensus(verdicts)
```

---

## Implementation Priority

1. **Lightweight vigilance** (2h) — Immediate value, no dependencies
2. **Boundary checking** (4h) — Leverages existing Honcho infrastructure
3. **Multi-agent verification** (8h) — Advanced, for complex tasks

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hallucination detection rate | >70% | Compare against human-annotated test set |
| False positive rate | <15% | Track user corrections after flagged responses |
| Latency overhead | <500ms | Measure add latency per detection call |
| User trust improvement | +40% | Survey-based assessment |

---

## References

1. **HalMit** — "Towards Mitigation of Hallucination for LLM-empowered Agents" (2025)
2. **FACTCHECKMATE** — "Preemptively Detecting and Mitigating Hallucinations in LMs" (EMNLP 2025)
3. **HADEMIF** — "Hallucination Detection and Mitigation via Dual-Space Calibration" (ICLR 2025)
4. **InEx** — "Hallucination Mitigation via Introspection and Cross-Modal Multi-Agent Collaboration" (AAAI 2025)
5. **GUARDIAN** — "Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling" (NeurIPS 2025)
