# acceptance-bench

## The hidden fragility of LLM benchmarks

**Most established LLM benchmarks use single fixed prompts per test case, despite research showing this approach can produce performance differences of up to 76 accuracy points from minor formatting changes alone.** The three benchmarks examined—SWE-bench, MMLU, and HumanEval—each take different approaches to prompt standardization, but none employs multiple prompt variations as standard practice. This creates a fundamental tension in the field: single prompts enable efficient comparison and reproducibility, while multiple prompts better capture true model capabilities and robustness. Recent innovations like PromptEval are making multi-prompt evaluation more feasible, achieving 100x cost reductions, but the community has yet to reach consensus on optimal benchmark design.

The significance extends beyond academic curiosity. When model rankings can flip based on arbitrary prompt formatting choices, and when format performance correlates weakly (0.2-0.4) between models, the entire enterprise of comparing LLMs on leaderboards becomes methodologically questionable. This matters for practitioners selecting models, researchers publishing comparisons, and the broader AI community tracking progress. The stakes are high: benchmark contamination studies reveal widespread overfitting, with some model families showing consistent 13% performance drops on fresh test data.

## How major benchmarks actually structure their prompts

The three canonical benchmarks represent a spectrum of standardization approaches, each with distinct implications for evaluation reliability.

**HumanEval stands as the most rigidly standardized.** Each of its 164 hand-crafted programming problems consists of exactly one fixed prompt: a Python function signature with type hints and a docstring containing the problem description and example inputs/outputs. The model must complete the function body. No variations exist, no few-shot examples are provided (though the docstring includes 2-3 input/output demonstrations as part of the specification), and every problem follows an identical structural format. This approach prioritizes consistency and computational efficiency—one prompt per problem, evaluated once.

**MMLU takes a middle path with standardized few-shot prompting.** Each of its 57 subjects uses a consistent template: "The following are multiple choice questions (with answers) about [subject]," followed by five fixed development examples demonstrating the format, then the test question. These five examples remain constant for each subject throughout evaluation. The format appears standardized, but research reveals significant sensitivity—testing across 24 different prompt styles produced 4-5% performance variance. Stanford HELM analysis found that "model creators have reported MMLU scores using non-standard prompting techniques" with "insufficient information about prompting templates," highlighting that even nominally standardized benchmarks face implementation inconsistencies.

**SWE-bench represents the least standardized approach**, delegating prompt construction entirely to implementers. The benchmark provides raw materials—GitHub issue text, codebase context, optional comments—but the actual prompt engineering varies by system. Different implementations use distinct styles (labeled `style-2`, `style-3`, `full_file_gen`) with variable context retrieval strategies (BM25, Oracle-based). As the original paper notes: "Per task instance, an AI system is given the issue text. The AI system should then modify the codebase in order to resolve the described issues." The wide latitude in prompt construction makes cross-system comparisons challenging and results less directly comparable.

Beyond these three, the broader ecosystem shows similar patterns. **GSM8K uses standardized 8-shot Chain-of-Thought prompts** through the EleutherAI harness. **BIG-Bench Hard employs the widest variation**, with research documenting 136-188 different prompt formats per task. **HELM approaches standardization differently**, using a taxonomy of 16 core scenarios with multiple metrics measured simultaneously, though it faces challenges when models are trained for specific formats like Claude's Human/Assistant structure. **MT-Bench uses 80 fixed multi-turn conversations** evaluated by GPT-4 as judge. **AlpacaEval focuses on single-turn instruction following** with GPT-4-based comparison to reference outputs.

The overarching pattern is clear: **none of these benchmarks employs multiple prompt variations as standard evaluation protocol**, though several have been tested with variations in robustness studies. Most benchmarks prioritize a single canonical prompt format, trading potential comprehensiveness for practical efficiency and reproducibility.

## The fundamental tension between efficiency and robustness

The debate over single versus multiple prompts reflects deeper questions about what benchmarks should measure and how computational resources should be allocated.

### Why single fixed prompts dominate current practice

Single prompts offer compelling practical advantages. **Computational efficiency tops the list**—one evaluation run per model rather than dozens or hundreds. For large models costing thousands of dollars per full benchmark run, this matters enormously. Development teams can iterate rapidly, testing changes quickly without waiting days for comprehensive evaluations. The approach also delivers perfect reproducibility in a narrow sense: given identical prompts, results replicate exactly. This enables clear historical comparisons and straightforward debugging when performance degrades.

From an implementation perspective, single prompts reduce engineering complexity. No need to generate diverse prompt sets, manage aggregation across variations, or explain why different statistics matter for different use cases. The simplicity extends to communication—reporting a single number is far easier than explaining performance distributions. For many real-world deployments, users do settle on specific prompt formats, making evaluation on that exact format practically relevant.

### The brittleness problem that undermines everything

But these advantages rest on a fragile foundation. **Research by Sclar et al. (2023) documented performance swings of up to 76 accuracy points** when evaluating LLaMA-2-13B across semantically equivalent prompts in few-shot settings. These aren't dramatic rewrites—minor formatting changes in spacing, punctuation, or separator tokens produced massive differences. The problem persists even when increasing model size, adding more few-shot examples, or applying instruction tuning.

The Mizrahi et al. (2023) study analyzing 6.5 million instances across 20 LLMs and 39 tasks found that **both absolute and relative performance vary dramatically across prompts**. The same model can rank first with one prompt format and last with a semantically equivalent alternative. Format performance correlates weakly (0.2-0.4) between models, meaning a prompt that works well for Model A may work poorly for Model B. This makes comparing models using an arbitrarily chosen fixed format methodologically questionable—the ranking might simply reflect prompt compatibility rather than genuine capability differences.

Additional brittleness emerges from model-specific training. Models fine-tuned for specific prompt structures (like Claude's Human/Assistant format) face systematic disadvantages on benchmarks using different conventions. Base models show different sensitivity patterns than instruction-tuned variants. The choice of prompt format inadvertently advantages models whose training aligned with that format, introducing unfairness that single-prompt evaluations cannot detect or correct.

The reproducibility benefit also proves somewhat illusory. While technically reproducible, a single-prompt score may not be meaningful or generalizable. Different benchmarks choosing different single prompts produce conflicting rankings. Reproducibility without reliability or validity is of limited value.

### Multiple prompts capture reality better but cost more

Multiple prompt variations address these weaknesses by providing richer information about model capabilities. Instead of a single potentially unrepresentative score, evaluations produce **performance distributions that reveal both typical performance and variance**. This robustness matters for high-stakes decisions—model selection, publication claims, deployment choices—where understanding the full capability envelope is critical.

The approach enables more sophisticated reporting. Rather than a single number, benchmarks can report:
- **Median (50th percentile)** representing typical performance
- **95th percentile** showing what expert prompt engineers might achieve  
- **5th percentile** indicating worst-case scenarios for novice users
- **Standard deviation** quantifying robustness

These statistics serve different stakeholders differently. LLM developers care about median performance and robustness across prompts. Downstream developers want to know the best achievable performance for their specific task. End users need to understand worst-case behavior. A single number serves none of these needs well.

Multiple prompts also better detect models optimized for narrow prompt patterns—a form of overfitting to evaluation conventions rather than genuine capability. Models showing high performance on one prompt but poor performance on variations may have memorized format-specific patterns. Robust models maintain more consistent performance across variations.

### The cost barrier is falling rapidly

Traditionally, the computational cost objection proved decisive. Evaluating 100 prompt variations requires 100x more compute than single-prompt evaluation—prohibitively expensive for many teams. But **recent innovations dramatically reduce this barrier**.

**PromptEval (Polo et al., 2024) achieves 100x compute savings** using Item Response Theory to estimate performance across 100+ prompts while evaluating only 2-4 prompts fully. The method borrows statistical strength across prompts and examples, accurately estimating performance distributions including quantiles. Validation on MMLU, BIG-Bench Hard, and LMentry showed the approach maintains accuracy while slashing costs.

Other efficiency techniques include stratified evaluation—using single prompts for rapid development, 10-20 prompts for intermediate checkpoints, and comprehensive multi-prompt evaluation only for final publication-quality results. Hybrid approaches report both single-prompt baseline scores for historical comparison and multi-prompt distributions for robustness assessment.

## Prompt diversity strategies and their implementation

When benchmarks do test robustness, they employ several systematic variation strategies, each targeting different aspects of prompt sensitivity.

**Paraphrasing-based variations** use linguistic transformations: synonym substitution, voice changes (active to passive), function word variations ("Pat gave a nice demo" → "Pat's demo was nice"), preposition modifications, and metaphor alternatives. Automated approaches leverage models like PEGASUS or T5 for paraphrase generation, or use LLMs with controlled diversity settings. These variations test whether models understand semantic content rather than surface form.

**Formatting variations** prove surprisingly impactful despite seeming trivial. Changes in line breaks, special characters (colons, dashes, double bars), punctuation placement, spacing patterns, and text casing can produce dramatic performance differences. The PromptEval study tested 100 MMLU variations with features including separator tokens (-, ::, ||), space variations, and operator changes—revealing that models are extraordinarily sensitive to these "spurious formatting features."

**Instruction style variations** reframe tasks in different ways: question format ("What is the answer?"), instruction format ("Answer the following question:"), or imperative style ("Provide the solution for..."). Context-first versus question-first ordering, explicit versus implicit instructions, and verbose versus concise formulations all impact results. These variations test adaptability to different communication styles.

**Few-shot example variations** explore different training signal configurations: varying the number of examples (0-shot through many-shot), selecting different example sets, permuting example ordering, or varying example difficulty progression. Chain-of-Thought variations add intermediate reasoning steps, which Wei et al. (2022) showed improved performance dramatically—BBH tasks went from below-human to above-human performance with CoT prompting.

Research benchmarks using these strategies employ substantial variation counts. The Sclar et al. MMLU study tested 100 prompt templates. BIG-Bench Hard experiments used 136-188 variations per task. The "State of What Art" study analyzing 6.5 million instances tested prompts across 39 tasks. For practical implementations, researchers recommend **10-20 variations for basic robustness assessment** and **50-100+ variations for comprehensive evaluation**.

Automated generation approaches scale these efforts. Template-based methods systematically traverse graphs of formatting features. **LLM-based generators** like PromptBreeder use evolutionary algorithms, OPRO employs LLMs as gradient-free optimizers, and GrIPS performs edit-based search with delete, swap, paraphrase, and addition operations.

## The overfitting crisis hiding in plain sight

A parallel threat undermines benchmark validity: models increasingly show evidence of training data contamination and prompt memorization, raising questions about whether reported performance reflects genuine capability or memorized patterns.

### Four levels of contamination severity

Xu et al. (2024) identified **a contamination taxonomy spanning four levels of increasing severity**. **Semantic contamination**—exposure to similar content on the same topic—is most subtle and hardest to detect. **Information contamination** involves exposure to metadata, time distributions, or label distributions. **Data-level contamination** means seeing benchmark examples without labels. **Label-level contamination**—full exposure including correct answers—is most severe but easiest to detect. Detection difficulty increases inversely with severity.

The **GSM1k study by Scala AI (2024) provides concrete evidence** of systematic overfitting. They created GSM1k to mirror GSM8K's style and complexity with fresh problems. Testing across multiple model families revealed widespread overfitting. The worst model showed a 13% performance drop on fresh data. Phi and Mistral families showed consistent overfitting across all model sizes. A positive correlation (r²=0.32) emerged between GSM8k generation probability and performance gap—models that could easily generate GSM8K problems showed larger drops on GSM1k. Notably, frontier models (Gemini, GPT, Claude) showed minimal overfitting, suggesting better training data management.

### Simple decontamination fails

Yang et al. (2023) demonstrated that **simple string matching using n-gram overlap is insufficient** for decontamination. Basic variations—paraphrasing, translation, minor edits—bypass standard decontamination measures. They showed a 13B model could achieve GPT-4-level performance on contaminated benchmarks when such variations weren't eliminated. The critical issue: models memorize prompt patterns and structural features, not just specific answers.

The "When Benchmarks Lie" study (Sun et al., 2025) tested 20 mitigation strategies on 5 benchmarks and found a **fundamental fidelity-resistance tradeoff**. Surface edits preserve task semantics but fail to prevent contamination exploitation. Deeper rewrites block memorization but distort the original task, making scores incomparable to the original benchmark. No strategy successfully preserves benchmark integrity while eliminating memorization—a sobering finding suggesting contamination may be fundamentally intractable for static benchmarks.

### Dynamic benchmarks as escape route

This realization has driven innovation in benchmark design. **LiveCodeBench continuously collects new coding problems** from competitive programming platforms after model training cutoffs. **LatestEval uses texts published within recent time windows**, ensuring freshness. **DyVal updates monthly** to test reasoning without contamination risk. These approaches trade historical comparability for evaluation integrity—earlier models cannot be fairly compared on later instances, but at least the evaluation measures genuine capability.

Private benchmarks kept confidential and isolated from public networks offer another approach, though they require trust and limit accessibility. Adversarial evaluation using RL or GANs to synthesize novel test cases shows promise. The community increasingly recognizes that **static public benchmarks have limited lifespan before contamination renders them unreliable**.

## Achieving fair comparison across diverse models

Fair model comparison proves surprisingly difficult when models undergo different training regimes and optimization for different prompt conventions.

### The format compatibility problem

Models trained with specific prompt structures systematically perform better with those structures. A model fine-tuned on prompts using "Human:" and "Assistant:" tags may underperform on benchmarks using "User:" and "System:" or no tags at all. This isn't a capability difference—it's format compatibility. Standard benchmarks using arbitrary format choices inadvertently favor models whose training aligned with those choices.

The weak correlation (0.2-0.4) in format performance across models exacerbates this. Format A might be optimal for Model X but suboptimal for Model Y. **Comparing them using only Format A lacks methodological validity**—the ranking may reflect format compatibility rather than underlying capability. Yet this is precisely how most leaderboards operate.

### Standardization efforts provide partial solutions

**HELM (Holistic Evaluation of Language Models)** by Stanford CRFM represents the most comprehensive standardization effort. It employs a top-down taxonomy approach defining 16 core scenarios plus 26 targeted scenarios covering question answering, information retrieval, summarization, reasoning, and specialized tasks. Crucially, HELM measures **7 metric categories simultaneously**: accuracy, calibration, robustness, fairness, bias, toxicity, and efficiency. This multi-metric approach ensures trade-offs become visible—a model might excel at accuracy while performing poorly on fairness or toxicity.

HELM achieved dramatic standardization improvements. Before HELM, models were evaluated on average 17.9% of core scenarios. After HELM, coverage reached 96.0% across 30 models on the same scenarios. All raw prompts and completions are released publicly for reproducibility. However, HELM still faces format compatibility challenges—standardized prompts may not work well for all models.

**EleutherAI's LM Evaluation Harness** provides complementary infrastructure. Its unified framework enables testing any causal language model on identical inputs using standardized procedures. With 60+ academic benchmarks, hundreds of subtasks, and flexible interfaces supporting multiple model types, the harness serves as a ground-truth evaluation location. Task versioning tracks changes with version numbers bumped for breaking changes and changelogs documenting modifications. This ensures long-term reproducibility and comparability.

### The standardization-flexibility tradeoff

Fixed architectures provide fair comparison, reproducibility, and scalability, but place enormous weight on initial prompt selection and may miss model-specific optimal performance. Flexible approaches allowing model-specific optimization capture best-case performance and reflect real-world usage diversity, but make fair comparison harder and increase complexity.

**Emerging best practice recommends reporting both**: standardized baseline scores for apples-to-apples comparison and model-optimized scores showing achievable performance, with full transparency about prompt selection methodology. This dual reporting acknowledges that different stakeholders need different information—researchers comparing capabilities want standardization, while practitioners deploying models want optimization guidance.

## Research-backed best practices for benchmark design

The academic community has converged on several key principles for robust benchmark design, synthesized from multiple influential studies.

### HELM's foundational principles

HELM established three core tenets. **Broad coverage with explicit recognition of incompleteness**: taxonomize the vast space of scenarios and metrics, clearly state what's missing (neglected English dialects, certain trustworthiness dimensions), and select a feasible subset based on coverage goals. This honesty about limitations helps users understand scope.

**Multi-metric measurement ensures important dimensions don't fall away.** Accuracy alone provides insufficient insight. Measuring calibration, robustness, fairness, bias, toxicity, and efficiency simultaneously—which HELM does 87.5% of the time—exposes trade-offs clearly. A model might achieve high accuracy but poor calibration or fairness, information lost in single-metric evaluation.

**Standardized conditions enable meaningful comparison.** All models benchmarked on identical scenarios with identical metrics under identical conditions, with full transparency through public release of raw prompts and completions. The "living benchmark" concept—continuous updates with new scenarios, metrics, and models—prevents obsolescence.

### Practical recommendations from contamination research

The benchmark data contamination literature provides actionable guidance. **Assume contamination risk exists for any public benchmark.** Implement detection methods combining multiple approaches: n-gram overlap (though insufficient alone), membership inference testing, perplexity comparison, chronological analysis of pre- versus post-training cutoff performance, and generation order analysis using statistical tests.

**Report contamination analysis transparently.** If contamination is detected, disclose it. If detection methods are limited, acknowledge uncertainty. The Sainz et al. (2023) position paper argues classical evaluation using annotated benchmarks is compromised and calls for community efforts to flag papers with contamination-compromised conclusions.

**Use versioning and updates aggressively.** Benchmark content should refresh regularly. DyVal's monthly updates and LiveCodeBench's continuous collection of new problems illustrate the approach. Accept that historical comparability will be limited—the integrity of measuring genuine current capability matters more than perfect continuity with contaminated earlier results.

### Guidelines for prompt selection and variation testing

When designing prompts, include core components systematically: context providing background, clearly defined objective, style specification, tone guidance, audience consideration, and response format description. Test across multiple strategies—zero-shot for innate ability, few-shot for learning from limited information, and Chain-of-Thought for complex reasoning tasks.

**The FormatSpread algorithm** (Sclar et al., 2023) offers a practical approach for rapid robustness evaluation. Sample plausible prompt formats for a task, rapidly evaluate across formats, and report an interval of expected performance rather than a single point estimate. This method requires no model weight access, making it applicable even for closed models.

**PromptEval** extends this with extreme efficiency. Using Item Response Theory to estimate performance across 100+ prompts while evaluating only 2-4 fully, the method provides quantile estimates (median, 95th percentile, 5th percentile) useful for analyzing both typical and tail behavior. Validated on MMLU, BIG-Bench Hard, and LMentry, it achieves roughly 100x compute savings while maintaining accuracy.

### Common pitfalls to avoid

The research literature identifies clear antipatterns. **Never use a single fixed prompt format for comparing all models** without testing variations. Don't assume prompt insensitivity—the evidence shows sensitivity is pervasive and severe. Avoid ignoring weak format-performance correlations between models, which invalidate single-format comparisons. Don't cherry-pick best-performing prompts without disclosure, and never compare models evaluated with different prompt formats without explicitly noting the limitation.

Instead, report performance ranges across formats, test with semantically equivalent variations, document prompt selection methodology thoroughly, include robustness metrics alongside accuracy, provide full prompt templates publicly for reproducibility, and version prompts with tracked changes over time.

## Synthesis: navigating the evaluation validity crisis

The accumulated evidence reveals a field in transition. Established benchmarks like MMLU, HumanEval, and SWE-bench largely rely on single fixed prompts, prioritizing efficiency and historical continuity. Yet research from 2023-2024 demonstrates this approach produces unreliable results—performance varies dramatically with prompt formatting, contamination is widespread, and model rankings depend heavily on arbitrary evaluation choices.

**The community faces a fundamental tradeoff without perfect resolution.** Single prompts enable rapid iteration and clear comparison but measure prompt compatibility as much as genuine capability. Multiple prompts better capture true robustness but traditionally impose prohibitive computational costs. Contamination detection and mitigation face an inherent fidelity-resistance tension—methods that preserve task semantics fail to prevent memorization exploitation, while methods that prevent memorization distort the task.

Recent innovations offer paths forward. PromptEval and similar techniques reduce multi-prompt evaluation costs by 50-100x, making robustness assessment practical. Dynamic benchmarks like LiveCodeBench and LatestEval maintain integrity by continuous refresh. Comprehensive frameworks like HELM establish standardized multi-metric evaluation. Transparency initiatives releasing full prompts and completions enable reproducibility and validation.

The emerging consensus points toward **layered evaluation strategies matched to evaluation goals**. Rapid development cycles can use efficient single-prompt evaluation. Intermediate checkpoints should include 10-20 prompt variations for robustness checks. High-stakes comparisons, publication claims, and leaderboard rankings demand comprehensive multi-prompt evaluation with contamination analysis and multi-metric assessment. Different stakeholders need different information—medians for typical performance, high quantiles for optimized deployment, low quantiles for worst-case robustness, and variance measures for reliability assessment.

Most critically, the field must embrace epistemic humility about benchmark validity. Every static benchmark has limited lifespan before contamination and overfitting undermine it. Every prompt choice introduces bias favoring certain models. Every aggregation method emphasizes certain performance aspects over others. Acknowledging these limitations openly, reporting them transparently, and continuously innovating evaluation methodology represents the path forward—not claiming to have solved the measurement problem, but rather managing its inherent difficulties thoughtfully and honestly.

## Conclusion: from benchmark scores to capability understanding

The illusion of objectivity in benchmark scores obscures deep methodological challenges. A model achieving 85% on MMLU conveys precision that research shows is largely false—change the prompt format slightly, and the score might be 81% or 89%. Test on fresh problems in the same style, and systematic overfitting might reveal a drop to 72%. Measure not just accuracy but calibration and robustness, and the model might show severe weaknesses hidden by the headline number.

What distinguishes the current moment is not the discovery that measurement is hard—that has always been true—but rather the systematic documentation of how severe the problems are and the development of practical solutions. Performance differences of 76 accuracy points from formatting changes, weak cross-model correlation in format performance, widespread contamination with 13% drops on fresh data, and fundamental tradeoffs in mitigation strategies collectively demand different evaluation practices.

The path forward requires embracing evaluation as an ongoing process rather than a fixed benchmark score. Models must be tested across prompt variations to understand robustness. Fresh test data must continually replace contaminated benchmarks. Multiple metrics must be measured simultaneously to expose trade-offs. Full transparency about prompts, procedures, and limitations must become standard. Statistical distributions must replace point estimates in high-stakes comparisons.

For practitioners, this means treating benchmark scores as rough guides rather than precise measurements. Test candidate models on your specific tasks with your actual prompt formats. Evaluate robustness to variations you expect in deployment. Understand that published scores may not reflect performance you'll observe. For researchers, it means higher standards for publication claims—multi-prompt testing, contamination analysis, comprehensive metric suites, and transparent disclosure of all evaluation choices.

The benchmarks that structure current LLM evaluation evolved during an earlier era when these problems were less well understood. They served important purposes in tracking progress and enabling comparison. But the field has outgrown them. The evaluation infrastructure must evolve to match our understanding of what these systems can do, how they fail, and what users actually need to know. That evolution is beginning, driven by research documenting the problems and developing solutions. The question is how quickly the community will adopt practices that match the complexity of the systems being evaluated.