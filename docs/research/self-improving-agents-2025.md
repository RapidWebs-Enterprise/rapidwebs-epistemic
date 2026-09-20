# Research Report: Self-Improving Agents & Reflection

**Date:** 2026-09-20  
**Author:** Lucien (RapidWebs)  
**Focus:** State-of-the-art in agent self-reflection, error recovery, and continuous improvement

---

## Executive Summary

Modern LLM agents can perform tasks well in isolation, but consistently fail when encountering errors or novel situations. This report examines 6 approaches to agent self-improvement through reflection, error recovery, and iterative learning.

**Key Finding:** Agents that can **reflect on failures** and **revise trajectories in real-time** significantly outperform those that simply retry from scratch.

---

## 1. Agent-R: Iterative Self-Training with Reflection

**Source:** arXiv:2501.11425

### Problem
Agents based on behavior cloning from experts cannot recover from errors in real-world applications.

### Solution
Monte Carlo Tree Search (MCTS) for **dynamic trajectory revision**

### Method
1. **Error identification:** Actor model identifies first error step in failed trajectory
2. **Trajectory splicing:** Connect error point with adjacent correct path from tree
3. **On-the-fly revision:** Correct errors before reaching end of trajectory
4. **Iterative self-training:** Continuously improve revision capability

### Key Innovation
- **Timely revision:** Don't wait until end of rollout — revise at first error
- **Model-guided critique:** Actor model identifies suitable revision points
- **Loop prevention:** Strategy avoids concatenating inconsistent trajectories

### Results
- +5.59% performance improvement
- Shorter average revision length
- Better error recognition over iterations
- Prevents cascading errors

### Implementation for rapidwebs-epistemic
```python
class AgentR_Insights:
    """
    Apply Agent-R principles to session-based learning.
    """
    
    def revise_session_trajectory(self, failed_session):
        # 1. Identify first error point
        error_point = self._identify_first_error(failed_session)
        
        # 2. Find correct alternative path
        alternative = self._find_correct_alternative(error_point)
        
        # 3. Splice trajectories
        revised = self._splice_trajectories(
            failed_session[:error_point],
            alternative
        )
        
        # 4. Store for future reference
        self._add_to_revision_library(revised)
        
        return revised
```

---

## 2. SAMULE: Multi-Level Reflection Synthesis

**Source:** EMNLP 2025

### Problem
Existing reflection methods generate low-quality reflections due to inadequate error analysis.

### Solution
Three-level reflection synthesis across complementary granularities

### Architecture

**Level 1: Micro (Single-Trajectory Learning)**
- Analyze individual failed trajectories against reference plans
- Identify immediate errors and generate targeted corrections
- Example: "You missed checking file permissions before writing"

**Level 2: Meso (Intra-Task Learning)**
- Examine multiple trajectories from same task
- Categorize error types and build error taxonomy
- Example: "Permission errors occur 60% of time in file operations"

**Level 3: Macro (Inter-Task Learning)**
- Cluster similar errors across diverse tasks
- Extract transferable insights
- Example: "File operation errors share pattern: always missing pre-check"

### Training
- Synthesize reflections at all levels
- Fine-tune retrospective model via SFT
- Foresight-based reflection for interactive settings

### Results
- Outperforms reflection-based baselines
- Strong performance on TravelPlanner, NATURAL PLAN, Tau-bench
- Simple SFT sufficient (no costly RL required)

### Implementation for rapidwebs-epistemic
```python
class SAMULE_Insights:
    """
    Implement multi-level reflection for session improvement.
    """
    
    def synthesize_reflection(self, session_history):
        # Micro: Individual session errors
        micro = self._analyze_trajectory(session_history)
        
        # Meso: Pattern across similar sessions
        meso = self._categorize_errors(session_history)
        
        # Macro: Transferable insights
        macro = self._extract_general_patterns(micro, meso)
        
        # Merge reflections
        return self._merge_reflections(micro, meso, macro)
```

---

## 3. DORA: Dynamic Optimization for Reflection

**Source:** COLING 2025

### Problem
"Early Stop Reflection" — effective reflection only happens in early iterations

### Root Cause
Static, task-independent reflection prompts become repetitive and unhelpful

### Solution
Dynamic prompt generation via small language model + Bayesian optimization

### Architecture
```
[Agent History] → [SLM Prompter] → [Reflection Prompt] → [Reflector LLM] → [Reflection Advice]
                      ↑                                              ↓
              [Bayesian Opt] ←──── [Performance Feedback]
```

### Key Components
1. **SLM Prompter:** Small open-source model generates reflection prompts
2. **Controlled text generation:** Uses few-shot examples + soft prompts
3. **Bayesian Optimization:**Tunes prompt generation based on:
   - Agent performance metrics
   - Reflection suggestion diversity
4. **Iterative adaptation:** Prompts evolve over time

### Results
- +19% success in MiniWoB++
- +9% in Alfworld
- Effective mitigation of early-stop pattern

### Implementation for rapidwebs-epistemic
```python
class DORA_Insights:
    """
    Implement dynamic reflection prompt generation.
    """
    
    def __init__(self):
        self.prompter = SmallLanguageModel()
        self.bo_optimizer = BayesianOptimizer()
    
    def generate_reflection_prompt(self, agent_history):
        # Get feedback metrics
        performance = self._measure_performance(agent_history)
        diversity = self._measure_diversity(agent_history)
        
        # Optimize prompt generation
        optimized_prompt = self.bo_optimizer.optimize(
            objective=lambda p: self._evaluate_prompt(p, performance, diversity)
        )
        
        # Generate task-adaptive prompt
        return self.prompter.generate(optimized_prompt)
```

---

## 4. RetroAct: Joint Policy Gradient Optimization

**Source:** NAACL 2025

### Problem
Fine-tuned agents lack real-time self-reflection capability

### Solution
Joint optimization of task-planning and self-reflection via combined IL + RL

### Architecture
```
Stage 1: Imitation Learning
  [Expert Data] → [Distill Planner + Reflector]
  
Stage 2: Joint Policy Gradient
  [Planner] ↔ [Reflector] (mutual optimization)
  Planner reward: Environment reward
  Reflector reward: Improvement from reflection
```

### Key Innovation
- **Mutual facilitation:** Optimizing one improves the other
- **Off-policy training:** More sample-efficient
- **IL regularization:** Prevents divergence from good behaviors

### Results
- Llama-7b based RetroAct exceeds larger models
- Eliminates dependency on closed-source LLMs
- Enables continuous evolution in new environments

---

## 5. Godel Agent: Self-Referential Self-Improvement

**Source:** arXiv (2025)

### Inspiration
Gödel's incompleteness theorem — system can modify its own rules

### Mechanism
- Agent recursively updates both policy (π) AND learning algorithm (I)
- At each step, entire codebase can be rewritten
- Driven solely by high-level objectives through prompting

### Process
1. Execute current policy
2. Evaluate performance
3. If improvement possible, rewrite logic
4. Integrate new logic into runtime
5. Repeat

### Results
- Continuous self-improvement over cycles
- Surpasses manually crafted agents
- Adapts to new tasks without retraining

### Implementation Considerations
- High risk: Code modification can introduce bugs
- Best for non-critical logic paths
- Requires robust rollback mechanisms

---

## 6. Reflection-Bench: Evaluating Epistemic Agency

**Source:** ICML 2025

### Seven Dimensions of Epistemic Agency
1. Prediction
2. Decision-making
3. Perception
4. Memory
5. Counterfactual thinking
6. Belief updating
7. Meta-reflection

### Key Finding
- SOTA LLMs show "rudimentary signs" of epistemic agency
- Significant limitations in meta-reflection
- Clear three-tier performance hierarchy across models

### Benchmark Tasks
- Long-term relevance
- Minimized data leakage
- Cognitive psychology inspired

---

## Comparative Analysis

| Method | Reflection Type | Learning Mechanism | Complexity | Scalability |
|--------|----------------|-------------------|------------|-------------|
| Agent-R | Trajectory revision | MCTS + SFT | Medium | High |
| SAMULE | Multi-level synthesis | SFT | Medium | High |
| DORA | Prompt optimization | Bayesian opt | Low | Very High |
| RetroAct | Joint optimization | IL + RL | High | Medium |
| Godel | Recursive self-modification | Prompt-driven | Very High | Low |

---

## Recommended Implementation Strategy

### Phase 1: Basic Reflection (1 day)
```python
class BasicReflection:
    """Simple session-end reflection."""
    
    def reflect_on_session(self, transcript):
        # Extract errors
        errors = self._extract_errors(transcript)
        
        # Generate lessons
        lessons = [f"Lesson: {self._formulate_lesson(e)}" for e in errors]
        
        # Store for future sessions
        self._store_lessons(lessons)
        
        return lessons
```

### Phase 2: Multi-Level Synthesis (2 days)
```python
class MultiLevelReflection:
    """SAMULE-inspired reflection."""
    
    def synthesize(self, sessions):
        micro = self._micro_analysis(sessions[-1])
        meso = self._meso_analysis(sessions[-5:])
        macro = self._macro_analysis(sessions)
        
        return self._merge(micro, meso, macro)
```

### Phase 3: Dynamic Adaptation (3 days)
```python
class AdaptiveReflection:
    """DORA-inspired dynamic prompts."""
    
    def __init__(self):
        self.prompt_optimizer = BayesianOptimizer()
    
    def get_reflection_prompt(self, session_type):
        optimized = self.prompt_optimizer.optimize(
            session_type, self._performance_metrics
        )
        return self._generate_prompt(optimized)
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Error recovery rate | >80% | % of errors corrected on retry |
| Reflection quality | >0.7 | Human-rated usefulness |
| Learning curve improvement | >30% | Performance over sessions |
| Loop prevention | >95% | % of trajectories without loops |

---

## References

1. **Agent-R** — "Training Language Model Agents to Reflect via Iterative Self-Training" (2025)
2. **SAMULE** — "Self-Learning Agents Enhanced by Multi-level Reflection" (EMNLP 2025)
3. **DORA** — "Dynamic Optimization Prompt for Continuous Reflection" (COLING 2025)
4. **RetroAct** — "Improving Retrospective Language Agents via Joint Policy Gradient" (NAACL 2025)
5. **Godel Agent** — "Self-Evolving Framework for LLM Agents" (2025)
6. **Reflection-Bench** — "Evaluating Epistemic Agency in LLMs" (ICML 2025)
