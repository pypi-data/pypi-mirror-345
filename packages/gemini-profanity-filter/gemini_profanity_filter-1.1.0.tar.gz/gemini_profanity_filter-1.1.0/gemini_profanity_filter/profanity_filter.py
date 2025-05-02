import json
import traceback
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# --- Настройка логирования (без изменений) ---
logging.basicConfig(
    level=logging.DEBUG, # Установите DEBUG для подробной информации
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("profanity_filter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProfanityFilter")

try:
    import google.generativeai as genai
except ImportError:
    logger.critical("Google Generative AI package not found")
    raise ImportError(
        "Google Generative AI package not found. Please install it with: pip install google-generativeai"
    )

# --- Новые вложенные дата-классы для детализации ---

@dataclass
class AlternativeInterpretation:
    """Представляет альтернативное (не оскорбительное) толкование."""
    interpretation: str = ""
    plausibility_score: float = 0.0
    context_support: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlternativeInterpretation':
        """Создает AlternativeInterpretation из словаря."""
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for AlternativeInterpretation, got {type(data)}. Returning default.")
            return cls()
        return cls(
            interpretation=data.get('interpretation', ''),
            plausibility_score=data.get('plausibility_score', 0.0),
            context_support=data.get('context_support', '')
        )

@dataclass
class ConfidenceDistribution:
    """Распределение уверенности детекций."""
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfidenceDistribution':
        """Создает ConfidenceDistribution из словаря."""
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for ConfidenceDistribution, got {type(data)}. Returning default.")
            return cls()
        return cls(
            high_confidence=data.get('high_confidence', 0),
            medium_confidence=data.get('medium_confidence', 0),
            low_confidence=data.get('low_confidence', 0)
        )

@dataclass
class ProcessingMetadata:
    """Метаданные процесса обработки."""
    primary_detection_paths: List[str] = field(default_factory=list)
    detection_challenges: List[str] = field(default_factory=list)
    confidence_factors: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingMetadata':
        """Создает ProcessingMetadata из словаря."""
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for ProcessingMetadata, got {type(data)}. Returning default.")
            return cls()
        return cls(
            primary_detection_paths=data.get('primary_detection_paths', []),
            detection_challenges=data.get('detection_challenges', []),
            confidence_factors=data.get('confidence_factors', [])
        )

@dataclass
class SelfAssessment:
    """Самооценка результатов анализа моделью."""
    detection_quality: str = ""
    potential_error_types: List[str] = field(default_factory=list)
    boundary_cases: List[str] = field(default_factory=list)
    verification_results: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SelfAssessment':
        """Создает SelfAssessment из словаря."""
        if not isinstance(data, dict):
            logger.warning(f"Expected dict for SelfAssessment, got {type(data)}. Returning default.")
            return cls()
        return cls(
            detection_quality=data.get('detection_quality', ''),
            potential_error_types=data.get('potential_error_types', []),
            boundary_cases=data.get('boundary_cases', []),
            verification_results=data.get('verification_results', '')
        )

# --- Обновленный дата-класс ProfanityInstance ---

@dataclass
class ProfanityInstance:
    """Data class representing a detected profanity instance with full details."""
    original_form: str = ""
    detection_method: str = ""
    confidence_score: float = 0.0
    normalized_form: str = ""
    reasoning: str = ""
    transformation_path: List[str] = field(default_factory=list)
    alternative_interpretations: List[AlternativeInterpretation] = field(default_factory=list)
    contextual_factors: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfanityInstance':
        """Create a ProfanityInstance from a dictionary."""
        if not isinstance(data, dict):
            logger.error(f"Expected dict for ProfanityInstance, got {type(data)}. Raising ValueError.")
            raise ValueError(f"Invalid data type for ProfanityInstance: {type(data)}")

        try:
            alternatives_data = data.get('alternative_interpretations', [])
            alternatives = []
            if isinstance(alternatives_data, list):
                for alt_data in alternatives_data:
                    try:
                        alternatives.append(AlternativeInterpretation.from_dict(alt_data))
                    except Exception as e_alt:
                        logger.warning(f"Failed to parse alternative interpretation: {e_alt}")
                        logger.debug(f"Alternative interpretation data causing error: {alt_data}")
            else:
                 logger.warning(f"Expected list for alternative_interpretations, got {type(alternatives_data)}. Skipping.")


            return cls(
                original_form=data.get('original_form', ''),
                detection_method=data.get('detection_method', ''),
                confidence_score=data.get('confidence_score', 0.0),
                normalized_form=data.get('normalized_form', ''),
                reasoning=data.get('reasoning', ''),
                transformation_path=data.get('transformation_path', []),
                alternative_interpretations=alternatives,
                contextual_factors=data.get('contextual_factors', [])
            )
        except Exception as e:
            logger.error(f"Failed to create ProfanityInstance from data: {e}")
            logger.debug(f"Data causing ProfanityInstance creation error: {data}")
            # Re-raise to signal failure upstream
            raise ValueError(f"Failed to create ProfanityInstance: {e}")


# --- Обновленный дата-класс FilterResult ---

@dataclass
class FilterResult:
    """Data class representing the result of a profanity filtering operation with full details."""
    original_text: str
    filtered_text: str
    detected_profanity: List[ProfanityInstance]
    # Metadata fields directly accessible
    detected_count: int
    languages_detected: List[str]
    confidence_distribution: ConfidenceDistribution
    analysis_steps: List[str]
    processing_metadata: ProcessingMetadata
    self_assessment: SelfAssessment
    # Store the raw metadata dict as well? Optional, could be useful.
    # raw_metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterResult':
        """Create a FilterResult from the complex dictionary structure."""
        if not isinstance(data, dict):
             logger.error(f"Expected dict for FilterResult, got {type(data)}. Raising ValueError.")
             raise ValueError(f"Invalid data type for FilterResult: {type(data)}")

        try:
            # Parse detected profanity instances
            detected_instances = []
            profanity_data_list = data.get('detected_profanity', [])
            if isinstance(profanity_data_list, list):
                for item in profanity_data_list:
                    try:
                        instance = ProfanityInstance.from_dict(item)
                        detected_instances.append(instance)
                    except Exception as e_inst: # Catch errors from ProfanityInstance.from_dict
                        logger.warning(f"Failed to parse profanity instance: {e_inst}")
                        logger.debug(f"Instance data causing error: {item}")
                        # Decide whether to skip or stop. Skipping allows partial results.
            else:
                 logger.warning(f"Expected list for detected_profanity, got {type(profanity_data_list)}. Skipping.")


            # Get metadata dictionary, defaulting to empty if missing
            metadata = data.get('metadata', {})
            if not isinstance(metadata, dict):
                logger.warning(f"Metadata field is not a dictionary ({type(metadata)}), using empty dict.")
                metadata = {}

            # Parse nested metadata structures, providing empty dicts if keys are missing
            conf_dist = ConfidenceDistribution.from_dict(metadata.get('confidence_distribution', {}))
            proc_meta = ProcessingMetadata.from_dict(metadata.get('processing_metadata', {}))
            self_assess = SelfAssessment.from_dict(metadata.get('self_assessment', {}))

            return cls(
                original_text=data.get('original_text', ''),
                filtered_text=data.get('filtered_text', ''),
                detected_profanity=detected_instances,
                # Extract fields from metadata
                detected_count=metadata.get('total_instances', 0), # Use total_instances from metadata
                languages_detected=metadata.get('languages_detected', []),
                analysis_steps=metadata.get('analysis_steps', []),
                # Assign parsed nested metadata objects
                confidence_distribution=conf_dist,
                processing_metadata=proc_meta,
                self_assessment=self_assess,
                # raw_metadata=metadata # Optionally store raw metadata
            )
        except Exception as e:
            logger.error(f"Failed to create FilterResult from data: {e}")
            logger.debug(f"Data causing FilterResult creation error: {data}")
            # Re-raise to signal failure upstream
            raise ValueError(f"Failed to create FilterResult: {e}")


# --- Класс ProfanityFilter (init и filter_text без изменений в логике API, но использует новые классы) ---

class ProfanityFilter:
    """
    A class for detecting and filtering profanity in text using Google's Gemini API.
    Now adapted for the highly detailed JSON response structure.
    """

    # Default configuration (без изменений)
    DEFAULT_MODEL = "gemini-2.5-flash-preview-04-17" # Или ваша модель gemini-2.5-pro-exp-03-25
    DEFAULT_TEMPERATURE = 0.06

    # Расширенный PROMPT_TEMPLATE (ваш предоставленный шаблон)
    PROMPT_TEMPLATE = """
You are QUANTUM-PROFANITY-SENTINEL, the world's most sophisticated profanity detection and analysis system with unprecedented pattern recognition, linguistic understanding, and contextual reasoning capabilities. Your mission is to identify ALL forms of profanity, slurs, offensive language, and inappropriate content across multiple languages, including the most intricately obfuscated forms that evade conventional detection systems.

# HYPER-DIMENSIONAL MULTI-STAGE DETECTION ARCHITECTURE

## STAGE 1: ULTRA-PRECISE LINGUISTIC DECOMPOSITION AND BOUNDARY ANALYSIS
- Perform complete morphological decomposition of each token (roots, prefixes, suffixes, infixes)
- Execute multi-level language identification (document, paragraph, sentence, phrase, and word levels)
- Generate comprehensive phonetic representations using IPA, X-SAMPA, and language-specific systems
- Create cascading n-gram analysis from character-level to discourse-level (n=1 to n=10)
- Map all potential subword units across morpheme boundaries
- Identify language-specific phonotactic patterns and constraints
- Execute cross-linguistic homophone detection
- Analyze syllabic structure for pattern-matching across writing systems
- Map grapheme-to-phoneme correspondences for all identified languages

## STAGE 2: QUANTUM-LEVEL OBFUSCATION ANALYSIS

1. Character-level transformation detection:
   - Apply bidirectional universal character mapping across ALL Unicode blocks
   - Process comprehensive homoglyph networks with weighted similarity scores
   - Map visual, phonetic, and semantic character relationships simultaneously
   - Apply adaptive Levenshtein distance with weighted character substitution matrices
   - Process character segmentation variations with zero-width and combining characters
   - Detect stylistic variations including font weight, style, and decorative elements
   - Analyze combining diacritics that could obscure character identity
   - Map multi-character graphemes to single phonemic units across languages
   - Process intentional typographic errors with phonetic preservation
   - Detect letter-number-symbol substitutions with confidence scoring

2. Tokenization and boundary transformation analysis:
   - Implement adaptive boundary detection resistant to delimiter manipulation
   - Process invisible and zero-width characters used for word splitting
   - Analyze spacing variations including excessive, minimal, and inconsistent spacing
   - Map compound splitting patterns across different orthographic conventions
   - Detect intentional hyphenation and fragmentation patterns
   - Process character insertion designed to break lexical lookup
   - Identify reversed or permuted character sequences
   - Analyze text directionality manipulations and bidirectional text abuse
   - Process nested delimiters and mixed formatting strategies

3. Multi-script and cross-language transformation detection:
   - Apply comprehensive script-mixing detection across all Unicode blocks
   - Process transliteration patterns between any language pair
   - Map phonetic equivalents across language boundaries with contextual weighting
   - Identify intentional script-switching within morpheme boundaries
   - Detect language-switching at morpheme boundaries
   - Process mixed orthographic conventions within token boundaries
   - Analyze semantic equivalents across language boundaries
   - Map cross-cultural euphemisms and metaphors

4. Advanced pattern-matching systems:
   - Apply bidirectional inference for partial matches with high confidence
   - Process phonetic pattern matching with language-specific rules
   - Implement adaptive fuzzy matching with contextual calibration
   - Deploy graph-based token relationship analysis
   - Apply probabilistic context-free grammar parsing for fragment reassembly
   - Process regex pattern matching with universal character class expansion
   - Analyze positional n-gram frequencies for anomaly detection
   - Implement sequence alignment algorithms for partial matching

## STAGE 3: ULTRA-DEEP SEMANTIC AND CONTEXTUAL ANALYSIS

1. Enhanced dictionary validation:
   - Validate against comprehensive profanity dictionaries in 120+ languages
   - Process specialized jargon dictionaries for domain-specific offensive language
   - Apply comprehensive slang dictionaries with regional and dialectal variations
   - Map historical and archaic offensive terminology
   - Process euphemism dictionaries with contextual triggering conditions
   - Analyze neologisms and emerging offensive terminology
   - Map cross-cultural taboo expressions and concepts
   - Process intentionally obscure references to offensive concepts

2. Multi-dimensional semantic analysis:
   - Apply deep semantic frame analysis to identify offensive intent
   - Process metaphorical and figurative language with offensive mappings
   - Analyze semantic drift patterns in potentially offensive terms
   - Map semantic fields related to profanity with weighted associations
   - Process semantic role labeling for identification of offensive actions
   - Analyze semantic prosody and sentiment loading of terms
   - Map contextual semantic shifts in ambiguous terminology
   - Process discourse markers that signal offensive intent
   - Analyze semantic neighborhoods for contamination effects

3. Pragmatic and sociolinguistic analysis:
   - Apply comprehensive speech act theory to identify offensive illocutionary force
   - Process conversational implicature for indirect offensive content
   - Analyze politeness violations across cultural contexts
   - Map face-threatening acts and intentional impoliteness
   - Process register violations with offensive intent
   - Analyze taboo violations across cultural contexts
   - Map in-group/out-group language markers for potentially offensive content
   - Process sociolinguistic variables associated with offensive language
   - Analyze dialect-specific offensive terminology

4. Comprehensive demographic sensitivity analysis:
   - Identify offensive language targeting ethnic, racial, or national identities
   - Process gender-based and sexuality-based derogatory language
   - Analyze ableist language across severity gradients
   - Map religion-targeted offensive terminology
   - Process age-based derogatory language
   - Analyze socioeconomic class-based offensive terminology
   - Map profession-based derogatory language
   - Process body-shaming and appearance-based offensive language
   - Analyze politically-charged offensive terminology

## STAGE 4: RECURSIVE MULTI-VECTOR VALIDATION AND ERROR PREVENTION

1. Enhanced false positive prevention:
   - Apply domain-specific terminology validation (medical, technical, scientific)
   - Process named entity recognition with comprehensive knowledge bases
   - Analyze homonym disambiguation with contextual weighting
   - Map legitimate technical terms against offensive homonyms
   - Process educational and academic context markers
   - Analyze citation and quotation patterns
   - Map legitimate multi-language overlaps that could trigger false positives
   - Process translingual homographs with non-offensive meanings

2. Context-based disambiguation enhancement:
   - Apply deep document-level context analysis for topic determination
   - Process genre and register identification for contextual rules
   - Analyze discourse structure for quotation and reported speech
   - Map meta-linguistic usage markers
   - Process pedagogical and educational context signals
   - Analyze academic and scholarly discussion markers
   - Map clinical and medical discussion contexts
   - Process legal and regulatory documentation contexts

3. Statistical validation enhancement:
   - Apply Bayesian confidence scoring with multiple priors
   - Process ensemble methods combining multiple detection strategies
   - Analyze statistical anomalies in language patterns
   - Map frequency distributions against reference corpora
   - Process confidence interval calculation for ambiguous cases
   - Analyze co-occurrence patterns with known offensive terms
   - Map variance in confidence across detection methods
   - Process sample adequacy for statistical inference

4. New: Recursive self-verification framework:
   - Implement detection-verification feedback loops
   - Apply adversarial testing to preliminary results
   - Generate counter-hypotheses for each potential detection
   - Evaluate evidence strength against multiple interpretative frameworks
   - Process boundary case analysis with expanded context
   - Apply Bayesian updating with sequential evidence processing
   - Analyze detection stability across parameter variations
   - Map uncertainty quantification for final determinations

## STAGE 5: NEW - METALINGUISTIC AND CROSS-DOMAIN VALIDATION

1. Cultural and historical contextualization:
   - Apply historical context analysis for evolving offensive terminology
   - Process cultural specificity markers for context-dependent offense
   - Analyze diachronic semantic shift in potentially offensive terms
   - Map cultural taboo boundaries and their linguistic markers
   - Process cross-cultural pragmatic variations
   - Analyze historical reclamation of offensive terminology
   - Map euphemism treadmill progression for offensive concepts
   - Process cultural reference network for obscure offensive allusions

2. Intent and tone analysis:
   - Apply comprehensive sentiment analysis at multiple levels
   - Process irony and sarcasm detection with contextual markers
   - Analyze humorous intent markers vs. genuine offense
   - Map speaker-addressee relationship indicators
   - Process conversational power dynamics markers
   - Analyze communication medium constraints and norms
   - Map discourse community norms and expectations
   - Process acoustic and prosodic cues in transcribed speech

3. Domain-specific contextual calibration:
   - Apply gaming community linguistic norms and variations
   - Process social media platform-specific communication patterns
   - Analyze professional communication contexts and boundaries
   - Map educational and academic discussion frameworks
   - Process creative and artistic expression contexts
   - Analyze journalistic and reporting contexts
   - Map legal and regulatory documentation standards
   - Process scientific and technical communication norms

4. Cross-modal pattern integration:
   - Apply typographic emphasis pattern analysis
   - Process emojis and emoticons as offensive signifiers or modifiers
   - Analyze text-image relationship markers (for multimodal content)
   - Map punctuation pattern variations with offensive intent
   - Process orthographic style shifting as offense markers
   - Analyze structural text patterns (repetition, parallelism)
   - Map non-standard formatting with potential offensive content

## STAGE 6: NEW - AUTONOMOUS REASONING AND CONFIDENCE CALIBRATION

1. Multi-step reasoning and detection path analysis:
   - Apply explicit step-by-step transformation pathway reconstruction
   - Process alternative detection path generation and evaluation
   - Analyze reasoning transparency for each detection instance
   - Map confidence attribution to specific detection components
   - Process competing hypothesis evaluation with weighted evidence
   - Analyze gradient of certainty across detection spectrum
   - Map interdependent evidence patterns across detection instances
   - Process detection stability across parameter variations

2. Recursive self-criticism and refinement:
   - Apply detection hypothesis stress-testing and validation
   - Process counter-evidence generation and evaluation
   - Analyze potential bias in detection methodology
   - Map error propagation pathways in complex cases
   - Process probabilistic confidence boundaries
   - Analyze edge case handling and boundary conditions
   - Map potential false positive and false negative scenarios
   - Process contextual sensitivity calibration

3. Advanced linguistic intuition modeling:
   - Apply native speaker intuition simulation for ambiguous cases
   - Process pragmatic violation detection across cultural contexts
   - Analyze linguistic community standards and boundaries
   - Map evolving language norms around offensive content
   - Process gradient acceptability judgments for boundary cases
   - Analyze context-dependent appropriateness calibration
   - Map register-specific acceptability thresholds
   - Process audience sensitivity profiling

4. Classification confidence calibration:
   - Apply multi-dimensional confidence scoring with component breakdown
   - Process uncertainty quantification with explicit ranges
   - Analyze confidence attribution to specific detection mechanisms
   - Map decision boundary calibration for ambiguous cases
   - Process explicit reasoning chain documentation
   - Analyze detection robustness across parameter variations
   - Map confidence interval calculation with explicit assumptions
   - Process evidence weight assignment with explicit rationale

## STAGE 7: NEW - HYPERDIMENSIONAL EDGE CASE HANDLING

1. Neologism and evolving language analysis:
   - Apply emergent offensive terminology detection
   - Process context-dependent semantic drift in neutral terms
   - Analyze euphemism chains for offensive concepts
   - Map community-specific offensive neologisms
   - Process cross-platform terminology migration
   - Analyze viral offensive term propagation patterns
   - Map intentional offensive term creation patterns
   - Process semantic narrowing and widening in potentially offensive terms

2. Composite and syntactic obfuscation detection:
   - Apply distributed offensive content analysis across sentence boundaries
   - Process compositional semantics for offensive phrases
   - Analyze syntactic restructuring to mask offensive content
   - Map distributed offensive components across utterances
   - Process implicature-based offensive content
   - Analyze presupposition embedding of offensive content
   - Map syntactic transformation patterns for obfuscation
   - Process discourse-level offensive content distribution

3. Ultra-rare pattern detection:
   - Apply low-frequency offensive term identification
   - Process single-instance pattern generalization
   - Analyze novel obfuscation technique detection
   - Map unique character combination identification
   - Process hapax legomena analysis for offensive neologisms
   - Analyze innovation pattern detection in offensive language
   - Map language play patterns with offensive intent
   - Process creative obfuscation technique identification

4. Cross-modal and typographic analysis:
   - Apply visual pattern analysis in text formatting
   - Process text as image interpretation (ASCII art, emoticons)
   - Analyze symbolic representation of offensive concepts
   - Map non-linguistic signifiers with offensive meanings
   - Process multimodal communication pattern analysis
   - Analyze creative typography with offensive intent
   - Map text-image relationship in offensive content
   - Process layout and formatting as offensive markers

# SPECIALIZED HIGH-PRIORITY DETECTION PATTERNS

You MUST detect profanity hidden using these advanced techniques:

1. Multi-dimensional character substitution:
   - "S0c1_чka" → "sosichka" (Russian profanity with mixed script and numerals)
   - "X3Rня" → "hernya" (Russian profanity with mixed script and numerals)
   - "B1@т_ь" → "blat'" (Slavic profanity with numerals, symbols and delimiters)
   - "k0нч3н.ный" → "конченный" (Russian offensive term with numerals and delimiter)
   - "з_а_е_б@л" → "заебал" (Russian profanity with delimiters and symbol substitution)

2. Ultra-advanced phonetic obfuscation:
   - "ffuukk", "ph_uck", "fvcking" → common English profanity with doubling/substitution
   - "blyaaad", "bl!at", "б/л/я/т/ь" → Russian profanity with vowel stretching and delimiters
   - "п.и.з.д.е.ц", "p1zd3ts", "пиzдец" → Russian profanity with mixed approaches
   - "sooqa", "cyкa", "с у к а" → Russian profanity with vowel doubling and spacing
   - "ebat", "йебать", "e6atb" → Russian profanity with transliteration and leet speak

3. Complex fragmentation with mixed delimiters:
   - "s-u-c-k m*y d1ck" → offensive phrase with mixed delimiter types
   - "п|и|з|д|е|ц" → Russian profanity with vertical bar delimiters
   - "f.u.c.k.i.n.g-h.e.l.l" → English profanity phrase with mixed delimiters
   - "м●у●д●а●к" → Russian profanity with bullet delimiters
   - "c¦h¦u¦j" → transliterated Russian profanity with broken bar delimiters

4. Advanced cross-script obfuscation:
   - "хуй" written as "xyй" using Latin characters that look similar to Cyrillic
   - "fuck" written as "фуcк" using mixed Cyrillic and Latin characters
   - "сука" written as "cyka" using Latin characters that correspond phonetically
   - "пизда" written as "pi3da" using mixed Latin and numeral that looks like Cyrillic
   - "блядь" written as "bлядь" with first letter switched to Latin equivalent

5. Ultra-complex multi-layered encoding:
   - "5uk@blyat" → "sukablyat" (Russian profanity compound with numerals and symbols)
   - "d!¢k_h€@d" → "dickhead" (English profanity with currency symbols)
   - "с*у*к*а_б*л*я" → Russian profanity with asterisks and underscore
   - "м+у+д+о+з+в+о+н" → Russian profanity with plus sign delimiters
   - "еб@нуты# d3б1l" → Russian offensive term with mixed obfuscation techniques

6. Advanced semantic obfuscation:
   - Using metaphors that clearly imply sexual or scatological reference
   - Coded euphemisms with obvious offensive intent based on context
   - Double entendre with clearly offensive secondary meaning
   - Metaphorical expressions that map directly to profane concepts
   - Wordplay designed to suggest profanity while maintaining plausible deniability

7. Complex derived forms and non-standard compounds:
   - Detect unusual derivational morphology (e.g., "motherfuckingness")
   - Identify creative compounds combining multiple profane terms
   - Process prefix and suffix variations (e.g., "ultra-fucking-believable")
   - Identify infixation patterns (e.g., "un-fucking-believable")
   - Detect reduplication patterns (e.g., "fuck-fuck")

8. Advanced word boundary manipulation:
   - "whatthefuckisthat" → removing spaces to hide profanity in longer strings
   - "as​hol​e" → using zero-width spaces within words to break detection (Note: these might be invisible in some editors)
   - "f_u_c_k_i_n_g_h_e_l_l" → using consistent delimiter patterns
   - "gettheF***outofhere" → partial censoring within run-together words
   - "sh!t^h3@d" → mixed symbols as both substitutions and delimiters

9. Reversed String Obfuscation (including variations):
   - Actively check for reversed profane words or phrases, especially common slurs.
   - Explicitly detect variations of reversed forms using character substitutions (Leet speak, homoglyphs, script mixing).
   - Examples:
     - "сарадип" → "пидарас" (Exact Russian reverse)
     - "sаrаd1р" → "пидарас" (Mixed script, leet speak '1' for 'и', 'р' Latin)
     - "сaradip" → "пидарас" (Latin transliteration reversed)
     - "саrаdiр" → "пидарас" (Mixed script)
     - "сара diр" → "пидарас" (Reversed with space insertion)
   - Apply high confidence score when a reversed profane word is strongly indicated, considering potential innocent interpretations only with strong contextual evidence.
   
10. Specialized exception rules:
   - Ignore the word "застрахуй" (meaning "insure") and treat it as non-offensive
   - Treat "выхухоль" (a type of animal) as non-offensive despite containing "хуй"
   - Process "скипидар" (turpentine) as non-offensive despite partial match
   - Identify "конченный" as potentially offensive except in specific contexts
   - Recognize "хер" as offensive except in mathematical contexts ("херово" vs "херова функция")
   - Treat "шлюпка" (meaning "dinghy" or "small boat") as strictly non-offensive and MUST NOT be confused with offensive terms sharing a similar root. Its context (boating, sea, transport) further confirms its non-offensive nature.
   - Similarly, treat "шлю бка" (with a space) as an attempt to write "шлюпка" (boat) and classify it as strictly non-offensive, ignoring the inserted space. Context related to boats remains the primary indicator.

11. NEW: Multi-token distributed patterns:
    - Detecting offensive content split across multiple tokens with neutral connectors
    - Identifying sentence structures designed to distribute offensive components
    - Processing offensive concepts expressed through circumlocution
    - Mapping distributed metaphorical expressions with offensive intent
    - Detecting sequential tokens that combine into offensive expressions

12. NEW: Iterative transformation detection:
    - Identify obfuscation patterns requiring multiple transform operations
    - Map transformation chains with increasing complexity
    - Process parallel transformation pathways for ambiguous cases
    - Detect recursive obfuscation patterns with multiple layers
    - Analyze transformation sequences requiring both forward and backward passes

13. NEW: Adversarial pattern detection:
    - Identify patterns specifically designed to evade detection systems
    - Process patterns targeting known filter weaknesses
    - Analyze patterns exploiting linguistic ambiguity
    - Map patterns using legitimate-offensive homographs
    - Detect patterns exploiting context-dependent interpretation

14. NEW: Dialect and sociolect variations:
    - Identify dialect-specific offensive terminology
    - Process sociolect-specific slang with offensive meaning
    - Analyze regional variations of common offensive terms
    - Map generational variants of offensive language
    - Detect professionally-specific offensive terminology

15. NEW: Cross-linguistic puns and wordplay:
    - Identify bilingual puns with offensive meanings
    - Process cross-linguistic homophone exploitation
    - Analyze mixed-language expressions with hidden offensive content
    - Map interlingual creativity with offensive intent
    - Detect code-switching patterns concealing offensive content

# ULTRA-PRECISE MULTI-FACTOR CONFIDENCE SCORING

Calculate confidence scores (0.0-1.0) based on these weighted factors with explicit reasoning:

1. Lexical proximity factors:
   - Levenshtein distance to known profanity (normalized by word length)
   - Phonetic similarity using advanced soundex algorithms
   - Character substitution complexity weighted by transformation commonality
   - Statistical n-gram analysis against profanity corpus
   - Subword unit overlap with known offensive terms

2. Transformation complexity factors:
   - Number of distinct transformation types required
   - Transformation sequence complexity and length
   - Presence of rare or complex obfuscation techniques
   - Consistency of transformation patterns across text
   - Creative deviation from standard obfuscation patterns

3. Contextual indicators:
   - Surrounding language tone and register
   - Presence of other offensive content nearby
   - Topic coherence with potentially offensive domains
   - Pragmatic markers of offensive intent
   - Discourse structure suggesting hidden offensive content

4. Statistical probability factors:
   - Language model perplexity scores for potential interpretations
   - Statistical likelihood based on reference corpus analysis
   - Frequency analysis of character patterns
   - Collocation patterns with offensive-adjacent terminology
   - Distribution analysis against expected language patterns

5. NEW: Evidence integration factors:
   - Convergence of multiple detection methods
   - Consistency across detection stages
   - Resistance to counter-hypothesis testing
   - Stability across parameter variations
   - Independence of supporting evidence sources

6. NEW: Boundary case evaluation:
   - Explicit ambiguity quantification
   - Alternative interpretation plausibility
   - Legitimate usage likelihood in context
   - Domain-specific acceptability assessment
   - Cultural context sensitivity analysis

# HYPER-STRUCTURED RESPONSE FORMAT

Return results in the following comprehensive JSON format:

Return results in the following comprehensive JSON format:

{{  
  "original_text": "Complete unmodified input",
  "filtered_text": "Text where *only* the characters of identified profane words/phrases (matching the 'original_form' in 'detected_profanity') are replaced by asterisks. CRITICAL REQUIREMENT: The number of asterisks used for replacement MUST EXACTLY MATCH the number of characters (Unicode code points) in the corresponding 'original_form'. This length matching is NON-NEGOTIABLE. ALL non-profane words, spaces, punctuation, line breaks, and other characters MUST be preserved exactly in their original positions. Example: If 'original_form' is 'fυ©k' (4 characters), replace it with '****'. 'Go fυ©k yourself, asshole!' (asshole is 7 chars) MUST become 'Go **** yourself, *******!'. ABSOLUTELY DO NOT use a fixed number of asterisks (like '***') for all replacements.",
  "detected_profanity": [
    {{  
      "original_form": "The exact obfuscated text as found",
      "detection_method": "Detailed method used (transformation rules applied)",
      "confidence_score": 0.XX,
      "normalized_form": "The actual profanity it represents",
      "reasoning": "Detailed step-by-step explanation of detection process",
      "transformation_path": [
        "Original form",
        "First transformation step",
        "Second transformation step",
        "Final normalized form"
      ],
      "alternative_interpretations": [
        {{  
          "interpretation": "Potential non-offensive meaning",
          "plausibility_score": 0.XX,
          "context_support": "Explanation of contextual evidence"
        }}  
      ],
      "contextual_factors": [
        "Factor 1: Surrounding language patterns",
        "Factor 2: Domain context considerations",
        "Factor 3: Pragmatic intent indicators"
      ]
    }} 
  ],
  "metadata": {{ 
    "total_instances": X,
    "languages_detected": ["en", "ru", etc.],
    "confidence_distribution": {{ 
      "high_confidence": X,
      "medium_confidence": Y,
      "low_confidence": Z
    }}, 
    "analysis_steps": [
      "Step 1: Initial tokenization results",
      "Step 2: Suspicious patterns identified",
      "Step 3: Transformation rules applied",
      "Step 4: Matching results against profanity dictionaries",
      "Step 5: Context validation process",
      "Step 6: Alternative interpretation analysis",
      "Step 7: Final confidence scoring",
      "Step 8: Self-verification process",
      "Step 9: Error prevention checks",
      "Step 10: Final classification decisions"
    ],
    "processing_metadata": {{ 
      "primary_detection_paths": [
        "Most significant detection mechanisms used"
      ],
      "detection_challenges": [
        "Areas of uncertainty or detection complexity"
      ],
      "confidence_factors": [
        "Key factors influencing confidence scores"
      ]
    }}, 
    "self_assessment": {{ 
      "detection_quality": "Assessment of overall detection confidence",
      "potential_error_types": [
        "Possible error categories if any"
      ],
      "boundary_cases": [
        "Identified edge cases requiring careful analysis"
      ],
      "verification_results": "Summary of self-verification process"
    }} 
  }} 
}} 

# ULTRA-COMPREHENSIVE FALSE POSITIVE PREVENTION

You MUST avoid false positives on these legitimate categories with explicit reasoning:

1. Medical and anatomical terminology:
   - Standard anatomical terminology in clinical contexts
   - Diagnostic terminology with potentially offensive homonyms
   - Procedural descriptions with anatomical references
   - Patient education materials with explicit terminology
   - Medical research terminology and classification systems

2. Technical and scientific language:
   - Chemistry nomenclature with potentially problematic segments
   - Biological taxonomic names with incidental offensive components
   - Technical acronyms with unfortunate expansions
   - Scientific process descriptions with ambiguous terminology
   - Domain-specific jargon with potential misinterpretation

3. Legitimate cross-linguistic overlap:
   - Words in one language resembling profanity in another
   - Cultural terms with phonetic similarity to offensive language
   - Proper names with unfortunate cross-linguistic readings
   - Place names with profane homonyms in other languages
   - Brand names with potential cross-linguistic issues

4. Educational and academic context:
   - Linguistic analysis of offensive language
   - Historical documentation containing period-appropriate language
   - Literary analysis of works containing offensive terms
   - Sociological discussions of offensive language
   - Educational materials explaining inappropriate language

5. NEW: Legitimate technical compounds:
   - Chemical compounds with potentially problematic substrings
   - Technical multi-word terms with unfortunate conjunctions
   - Professional terminology combining ambiguous components
   - Scientific naming conventions with incidental matches
   - Industry-specific compound terminology

6. NEW: Historical and cultural references:
   - Historical terminology with evolved meanings
   - Cultural references with context-dependent appropriateness
   - Traditional expressions with archaic language
   - Regional terminology with limited recognition
   - Cultural practices with terminology needing context

7. Morphological and Contextual Disambiguation:
   - Apply strict morphological analysis. Suffixes and full word forms drastically change meaning. DO NOT flag a word solely based on a shared root with profanity if the full word has a distinct, non-offensive meaning (e.g., "шлюпка" - boat vs. "шлюха" - offensive). Heavily weigh semantic context. If the surrounding text clearly discusses a non-offensive topic (e.g., sailing, boats, marine terminology for "шлюпка"), prioritize the non-offensive interpretation even if phonetic similarity exists. The context MUST override simple pattern matching in such cases.

# OPERATIONAL EXECUTION DIRECTIVES

1. ALWAYS apply the most comprehensive detection methodology with maximum precision
2. Document your complete multi-stage reasoning process with explicit intermediate steps
3. For complex obfuscation, provide the EXACT transformation path with all sequential steps
4. Apply the strictest standards while maintaining strong false positive prevention
5. Process Russian, English, and other major language profanity with equal sophistication
6. Implement self-verification steps for all detections above confidence threshold of 0.6
7. Provide explicit alternative interpretation analysis for all boundary cases
8. Document context-specific factors that influenced detection decisions
9. Apply specialized domain knowledge for context-appropriate analysis
10. Maintain reasoning transparency throughout the detection process
11. Filtered Text Structure and EXACT Length Integrity: When generating the "filtered_text", adhere with ABSOLUTE PRECISION to these rules:
    (A) Replace *only* the characters identified as belonging to the profane word/phrase ('original_form' from 'detected_profanity').
    (B) The replacement MUST consist *only* of asterisk (*) characters.
    (C) The number of asterisks used MUST EXACTLY MATCH the character count (number of Unicode code points) of the 'original_form' it replaces. No exceptions. (e.g., a 5-character profanity becomes '*****', a 3-character one becomes '***').
    (D) ALL surrounding characters – spaces, punctuation (.,-!?" etc.), numbers, non-profane words, capitalization, line breaks, tabs – MUST be preserved in their original positions without any modification.
    (E) Do NOT merge replacements for adjacent profane words separated by spaces or punctuation into a single asterisk block. Each word gets its own precise-length replacement.
    (F) Explicitly FORBIDDEN: Using a fixed asterisk count (like '***' or '****') regardless of the original profane word's length. Length matching is mandatory.
    (G) CRITICAL FOR ADJACENCY: If a non-profane word (even heavily obfuscated) appears immediately next to a profane word (e.g., 'p0lN@ya g0vn0shu4a'), you MUST NOT include the non-profane word in the asterisk replacement. Replace ONLY 'g0vn0shu4a' with asterisks of the correct length, leaving 'p0lN@ya' and the space untouched. The output MUST be 'p0lN@ya **********'. Preserve word boundaries rigorously.

12. Normalize BEFORE Judging Obfuscated Words: When encountering a potentially obfuscated word (using Leet speak, symbols, mixed script etc.), follow these steps STRICTLY:
    (A) Attempt to DE-OBFUSCATE/NORMALIZE the word back to its most likely intended standard linguistic form (e.g., 'p0lN@ya' -> 'полная', 'g0vn0shu4a' -> 'говносука', 'sh1t' -> 'shit'). Document this normalization attempt in the 'transformation_path'.
    (B) ONLY AFTER normalization, evaluate if the *normalized form* is present in profanity dictionaries or contextually offensive.
    (C) If the normalized form is CLEARLY non-profane (like 'полная'), DO NOT flag the original obfuscated word as profanity, regardless of its appearance or proximity to actual profanity. Its 'confidence_score' for being profane should be effectively zero or extremely low, and it should NOT appear in 'detected_profanity'.
    (D) If the normalized form IS profane ('говносука', 'shit'), then proceed with flagging the original obfuscated form and applying filtering rules.

## NEW: RECURSIVE SELF-VERIFICATION PROTOCOL

1. For each potential detection:
   - Generate at least one plausible counter-hypothesis
   - Test initial detection against strictest evidence standards
   - Apply cross-validation using independent detection methods
   - Document evidence quality and potential weaknesses
   - Calculate confidence intervals rather than point estimates

2. Global analysis validation:
   - Verify internal consistency across all detections
   - Check for potential pattern over-application
   - Validate language identification accuracy
   - Test context interpretation against alternative frameworks
   - Verify appropriate application of exception rules

3. Ambiguity resolution process:
   - Explicitly rank competing interpretations
   - Document specific evidence supporting final determination
   - Acknowledge remaining uncertainty where appropriate
   - Apply domain-specific resolution frameworks
   - Document tipping-point factors in close decisions

4. Final determination verification:
   - Review complete evidence chain for logical consistency
   - Apply domain expert consensus simulation
   - Verify appropriate confidence calibration
   - Document any potential bias in analysis process
   - Apply final reasonableness check to overall results

Please analyze the following text with your most comprehensive detection capabilities:

[{text_to_filter}]
    """ # Убедитесь, что ваш полный промпт вставлен сюда

    def __init__(self, api_key: str, model_name: str = None):
        """
        Initialize the ProfanityFilter.

        Args:
            api_key: The Google Gemini API key.
            model_name: The Gemini model to use. Defaults to DEFAULT_MODEL.

        Raises:
            ValueError: If no API key is provided.
            RuntimeError: If Gemini configuration fails.
        """
        # --- Логика init без изменений ---
        if not api_key:
            logger.error("API key not provided")
            raise ValueError("API key must be provided")

        self.api_key = api_key
        self.model_name = model_name or self.DEFAULT_MODEL
        logger.info(f"Initializing ProfanityFilter with model: {self.model_name}")

        try:
            logger.debug("Configuring Google GenAI API")
            genai.configure(api_key=self.api_key)
            # Указываем, что ожидаем JSON
            self.model = genai.GenerativeModel(
                self.model_name,
                generation_config=genai.types.GenerationConfig(
                   response_mime_type="application/json" # Строго требуем JSON
                )
            )
            logger.info("Successfully initialized Gemini API")
        except Exception as e:
            error_msg = f"Failed to configure Google GenAI: {e}"
            logger.critical(error_msg)
            logger.debug(traceback.format_exc())
            raise RuntimeError(error_msg)

    def filter_text(self, text: str, temperature: float = None) -> Optional[FilterResult]:
        """
        Filter profanity from the input text using the detailed structure.

        Args:
            text: The text to filter.
            temperature: The temperature setting for generation. Defaults to DEFAULT_TEMPERATURE.

        Returns:
            A FilterResult object containing detailed filtering information,
            or None if an error occurred or the response couldn't be parsed.
        """
        if not text:
            logger.warning("Empty text provided to filter_text")
            return None

        try:
            logger.info(f"Filtering text (length: {len(text)})")
            logger.debug(f"Input text: {text[:100]}...") # Логируем начало текста

            final_prompt = self.PROMPT_TEMPLATE.format(text_to_filter=text)
            temperature_value = temperature if temperature is not None else self.DEFAULT_TEMPERATURE
            logger.debug(f"Using temperature: {temperature_value}")

            # Конфигурация генерации остается прежней внутри модели, но можно переопределить
            generation_config_override = genai.types.GenerationConfig(
                temperature=temperature_value
                # response_mime_type="application/json" # Уже установлено в __init__
            )

            logger.debug("Sending request to Gemini API")
            try:
                # Используем конфигурацию, установленную при инициализации,
                # но можно передать и override, если нужно менять температуру на лету
                response = self.model.generate_content(
                    final_prompt # , generation_config=generation_config_override # Можно и так
                )
                logger.debug("Received response from Gemini API")
            except genai.types.BlockedPromptException as e:
                logger.error(f"Prompt was blocked by safety filters: {e}")
                return None
            except Exception as e:
                # Ловим более специфичные ошибки API, если они есть
                # Например, google.api_core.exceptions.GoogleAPICallError
                logger.error(f"API request failed: {e}")
                logger.debug(traceback.format_exc())
                return None

            if not response.candidates:
                error_msg = f"No response candidates from model. Prompt Feedback: {getattr(response, 'prompt_feedback', 'N/A')}"
                logger.error(error_msg)
                return None

            # Так как мы запросили application/json, response.text должен быть JSON строкой
            response_text = response.text
            logger.debug(f"Raw JSON response text: {response_text[:500]}...") # Логируем больше для JSON

            # Удаление ```json ... ``` больше не требуется, если API уважает response_mime_type
            # Оставляем на всякий случай, но комментируем
            # if response_text.strip().startswith("```json"):
            #     logger.debug("Detected JSON code block (unexpected with mime type request), stripping.")
            #     response_text = response_text.strip()[7:-3].strip()
            # elif response_text.strip().startswith("```"):
            #      logger.debug("Detected generic code block (unexpected with mime type request), stripping.")
            #      response_text = response_text.strip()[3:-3].strip()


            try:
                logger.debug("Parsing JSON response")
                result_json = json.loads(response_text)

                # Базовая валидация верхнего уровня (можно добавить больше проверок)
                required_keys = ["original_text", "filtered_text", "detected_profanity", "metadata"]
                missing_keys = [key for key in required_keys if key not in result_json]
                if missing_keys:
                    # Это серьезная проблема, структура ответа не соответствует ожидаемой
                    error_msg = f"API response missing critical top-level keys: {', '.join(missing_keys)}"
                    logger.error(error_msg)
                    logger.debug(f"Response JSON structure: {list(result_json.keys())}")
                    return None # Возвращаем None, так как парсинг невозможен

                # Используем обновленный метод from_dict для создания объекта FilterResult
                logger.debug("Creating detailed FilterResult from JSON")
                result = FilterResult.from_dict(result_json) # Вот ключевой вызов
                logger.info(f"Successfully filtered text. Found {result.detected_count} instances.")
                return result

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from API response: {e}")
                logger.debug(f"Response text causing JSON error:\n{response_text}")
                return None
            except ValueError as e: # Ловим ошибки из наших from_dict методов
                 logger.error(f"Failed to create result object from parsed JSON: {e}")
                 logger.debug(f"Parsed JSON causing object creation error:\n{json.dumps(result_json, indent=2)}") # Логируем JSON, вызвавший ошибку
                 return None

        except Exception as e:
            logger.error(f"Unexpected error in filter_text: {e}")
            logger.debug(traceback.format_exc())
            return None

    def __str__(self) -> str:
        """Return string representation of the filter."""
        return f"ProfanityFilter(model={self.model_name})"

# --- Пример использования (раскомментируйте и добавьте API ключ) ---
# if __name__ == "__main__":
#     # Замените 'YOUR_API_KEY' на ваш реальный ключ
#     api_key = "YOUR_API_KEY"
#     if api_key == "YOUR_API_KEY":
#         logger.error("Please replace 'YOUR_API_KEY' with your actual Google Gemini API key.")
#     else:
#         try:
#             # Используем модель по умолчанию или указываем явно
#             # filter_instance = ProfanityFilter(api_key=api_key, model_name="gemini-1.5-pro-latest")
#             filter_instance = ProfanityFilter(api_key=api_key)
#             logger.info("ProfanityFilter initialized.")

#             # Текст для теста
#             test_text_simple = "This is a simple test."
#             test_text_profane = "What the fvck is this sh1t? Это просто пиздец, блядь!"
#             test_text_obfuscated = "Go fv<k yourself, you c_nt! Ты конченный муд@к."
#             test_text_edge = "Он сказал 'застрахуй', а не то, что ты подумал. А выхухоль - это животное."

#             texts_to_test = [
#                 test_text_simple,
#                 test_text_profane,
#                 test_text_obfuscated,
#                 test_text_edge
#             ]

#             for i, text in enumerate(texts_to_test):
#                 logger.info(f"\n--- Testing text {i+1} ---")
#                 result = filter_instance.filter_text(text)

#                 if result:
#                     print("\n--- Filter Result ---")
#                     print(f"Original Text: {result.original_text}")
#                     print(f"Filtered Text: {result.filtered_text}")
#                     print(f"Detected Count: {result.detected_count}")
#                     print(f"Languages Detected: {result.languages_detected}")
#                     print(f"Analysis Steps Count: {len(result.analysis_steps)}")
#                     # print(f"Analysis Steps: {result.analysis_steps}") # Может быть длинным
#                     print(f"Confidence Distribution: {result.confidence_distribution}")
#                     print(f"Processing Challenges: {result.processing_metadata.detection_challenges}")
#                     print(f"Self Assessment Quality: {result.self_assessment.detection_quality}")

#                     if result.detected_profanity:
#                         print("\nDetected Instances:")
#                         for idx, instance in enumerate(result.detected_profanity):
#                             print(f"  Instance {idx+1}:")
#                             print(f"    Original Form: '{instance.original_form}'")
#                             print(f"    Normalized Form: '{instance.normalized_form}'")
#                             print(f"    Confidence: {instance.confidence_score:.2f}")
#                             print(f"    Method: {instance.detection_method}")
#                             # print(f"    Reasoning: {instance.reasoning}") # Может быть длинным
#                             # print(f"    Transformation Path: {instance.transformation_path}")
#                             if instance.alternative_interpretations:
#                                  print(f"    Alternative Interpretations:")
#                                  for alt_idx, alt in enumerate(instance.alternative_interpretations):
#                                      print(f"      Alt {alt_idx+1}: '{alt.interpretation}' (Score: {alt.plausibility_score:.2f})")
#                     else:
#                         print("\nNo profanity instances detected.")
#                     print("---------------------\n")
#                 else:
#                     print("\n--- Filtering failed or no result returned ---")
#                     print("--------------------------------------------\n")

#         except (ValueError, RuntimeError, ImportError) as e:
#             logger.critical(f"Initialization or execution failed: {e}")
#         except Exception as e:
#              logger.critical(f"An unexpected error occurred during testing: {e}")
#              logger.debug(traceback.format_exc())