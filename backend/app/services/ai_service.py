"""
=============================================================================
AI SERVICE - OpenAI GPT-4 Integration for Resume Generation
=============================================================================

PURPOSE:
    This service handles all AI-powered operations for SmartCareer AI.
    It acts as the bridge between our application and OpenAI's GPT-4 API.

WHY THIS ARCHITECTURE?
    - Single Responsibility: All AI logic in one place
    - Testability: Easy to mock for unit tests
    - Reusability: Any part of the app can use AI features
    - Maintainability: Changes to AI logic don't affect other code

FEATURES:
    ✓ OpenAI client initialization with validation
    ✓ Resume generation from user data
    ✓ Token usage tracking for cost monitoring
    ✓ Retry logic with exponential backoff
    ✓ Comprehensive error handling
    ✓ Detailed logging at every step

USAGE:
    from app.services.ai_service import AIService
    
    # Create service instance
    ai_service = AIService()
    
    # Generate a resume
    result = await ai_service.generate_resume_from_data(user_data)

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard library imports
import json                          # For parsing JSON responses from GPT
import logging                       # For logging operations and errors
from typing import Dict, Any, List, Optional  # Type hints for better code clarity
from datetime import datetime        # For timestamps in usage tracking
from dataclasses import dataclass    # For structured data classes

# Third-party imports
from openai import (
    AsyncOpenAI,      # Async client for non-blocking API calls
    OpenAIError,      # Base exception for OpenAI errors
    RateLimitError,   # Thrown when we hit API rate limits
    APIError,         # General API errors (network, server issues)
    AuthenticationError,  # Invalid API key
)

# Tiktoken: OpenAI's tokenizer library (optional)
# WHY? We need to count tokens BEFORE sending to estimate costs
#      and prevent exceeding context limits
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None

# Tenacity: Retry library with advanced features
# WHY? APIs fail sometimes. Instead of crashing, we retry intelligently
#      with exponential backoff (wait longer between each retry)
from tenacity import (
    retry,                    # Decorator to add retry logic
    stop_after_attempt,       # Stop after N attempts
    wait_exponential,         # Wait 1s, then 2s, then 4s, etc.
    retry_if_exception_type,  # Only retry on specific exceptions
)

# Local imports
from app.config import settings  # Application configuration


# =============================================================================
# LOGGING SETUP
# =============================================================================
# WHY configure logging here?
# - Centralized logging for all AI operations
# - Easy to adjust log level for debugging vs production
# - Logs help trace issues in production without debugger access

logger = logging.getLogger(__name__)

# Set up console handler with formatting
# WHY detailed format? In production, we need timestamps and log levels
# to trace issues across multiple requests
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)

# Add handler if not already added
# WHY check? Prevents duplicate log entries if module is imported multiple times
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================
# WHY custom exceptions?
# - More specific error handling in calling code
# - Clearer error messages for debugging
# - Proper error categorization for API responses
# - Allows catching specific error types (e.g., rate limit vs auth error)

class AIServiceError(Exception):
    """
    Base exception for all AI service errors.
    
    WHY a base class?
    Allows catching ANY AI error with a single except clause:
        try:
            await ai_service.generate_resume(...)
        except AIServiceError as e:
            # Handle any AI-related error
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception with a message and optional details.
        
        Args:
            message: Human-readable error description
            details: Additional context for debugging (logged but not exposed to users)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        
        # Log the error immediately when it's created
        # WHY? Ensures we capture all errors, even if not properly handled upstream
        logger.error(f"AIServiceError: {message}", extra={"details": details})


class AIConfigurationError(AIServiceError):
    """
    Raised when the AI service is not properly configured.
    
    WHEN THROWN:
    - Missing OPENAI_API_KEY
    - Invalid API key format
    - Unsupported model specified
    
    HOW TO FIX:
    Check your .env file and ensure OPENAI_API_KEY is set correctly.
    """
    pass


class AIGenerationError(AIServiceError):
    """
    Raised when AI content generation fails.
    
    WHEN THROWN:
    - API returns an error response
    - Response cannot be parsed as JSON
    - Response is missing expected fields
    
    HOW TO FIX:
    Usually transient - retry the request. If persistent, check the prompt.
    """
    pass


class AIRateLimitError(AIServiceError):
    """
    Raised when OpenAI rate limits are exceeded.
    
    WHEN THROWN:
    - Too many requests per minute
    - Token limit exceeded for the billing period
    
    HOW TO FIX:
    Wait and retry, or upgrade your OpenAI plan.
    """
    pass


class AIValidationError(AIServiceError):
    """
    Raised when input data fails validation.
    
    WHEN THROWN:
    - Required fields are missing
    - Data format is incorrect
    - Values are out of acceptable range
    
    HOW TO FIX:
    Check the input data matches the expected schema.
    """
    pass


# =============================================================================
# DATA CLASSES FOR TYPE SAFETY
# =============================================================================
# WHY dataclasses?
# - Enforce structure on data flowing through the system
# - IDE autocompletion and type checking
# - Self-documenting code
# - Immutable by default (with frozen=True)

@dataclass
class ExperienceEntry:
    """
    Represents a single work experience entry.
    
    WHY a separate class?
    Ensures all experience entries have the same structure,
    preventing KeyError bugs when accessing fields.
    """
    company: str
    position: str
    duration: str
    description: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {
            "company": self.company,
            "position": self.position,
            "duration": self.duration,
            "description": self.description
        }


@dataclass
class EducationEntry:
    """
    Represents a single education entry.
    """
    institution: str
    degree: str
    year: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {
            "institution": self.institution,
            "degree": self.degree,
            "year": self.year
        }


@dataclass
class ResumeInputData:
    """
    Structured input data for resume generation.
    
    WHY this structure?
    - Validates all required fields are present
    - Provides type hints for IDE support
    - Documents the expected input format
    - Easy to extend with new optional fields
    """
    name: str
    email: str
    phone: str
    skills: List[str]
    experience: List[ExperienceEntry]
    education: List[EducationEntry]
    
    # Optional fields with defaults
    summary: Optional[str] = None
    target_job: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResumeInputData":
        """
        Create instance from dictionary (e.g., from JSON request).
        
        WHY a factory method?
        - Handles nested object creation (experience, education)
        - Provides a single place to validate and transform input
        - Makes testing easier with dictionary inputs
        
        Args:
            data: Dictionary containing resume data
            
        Returns:
            ResumeInputData instance
            
        Raises:
            AIValidationError: If required fields are missing or invalid
        """
        logger.debug(f"Parsing resume input data: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ["name", "email", "phone", "skills", "experience", "education"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            raise AIValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields, "received_fields": list(data.keys())}
            )
        
        # Parse experience entries
        # WHY try/except here? To give clear error messages if structure is wrong
        try:
            experience = [
                ExperienceEntry(
                    company=exp.get("company", ""),
                    position=exp.get("position", ""),
                    duration=exp.get("duration", ""),
                    description=exp.get("description", "")
                )
                for exp in data.get("experience", [])
            ]
        except (TypeError, AttributeError) as e:
            raise AIValidationError(
                "Invalid experience format. Expected list of objects.",
                details={"error": str(e), "received": data.get("experience")}
            )
        
        # Parse education entries
        try:
            education = [
                EducationEntry(
                    institution=edu.get("institution", ""),
                    degree=edu.get("degree", ""),
                    year=edu.get("year", "")
                )
                for edu in data.get("education", [])
            ]
        except (TypeError, AttributeError) as e:
            raise AIValidationError(
                "Invalid education format. Expected list of objects.",
                details={"error": str(e), "received": data.get("education")}
            )
        
        logger.debug(f"Successfully parsed: {len(experience)} experience entries, {len(education)} education entries")
        
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            skills=data["skills"],
            experience=experience,
            education=education,
            summary=data.get("summary"),
            target_job=data.get("target_job")
        )


# =============================================================================
# TOKEN USAGE TRACKER
# =============================================================================
# WHY track tokens?
# - OpenAI charges per token ($0.01-0.03 per 1K tokens for GPT-4)
# - Helps budget and monitor costs
# - Required for implementing usage limits per user
# - Useful for optimizing prompts (shorter = cheaper)

class TokenUsageTracker:
    """
    Tracks OpenAI API token usage for cost monitoring.
    
    HOW TOKENS WORK:
    - A token is roughly 4 characters or 0.75 words
    - "Hello world" = 2 tokens
    - GPT-4 Turbo: ~$0.01 per 1K input tokens, ~$0.03 per 1K output tokens
    """
    
    def __init__(self):
        """Initialize counters and history."""
        self.total_prompt_tokens = 0      # Tokens we sent to OpenAI
        self.total_completion_tokens = 0  # Tokens OpenAI sent back
        self.total_requests = 0           # Number of API calls
        self.request_history: List[Dict[str, Any]] = []  # Detailed history
        
        logger.debug("TokenUsageTracker initialized")
    
    def add_usage(
        self, 
        prompt_tokens: int, 
        completion_tokens: int,
        model: str,
        operation: str
    ) -> Dict[str, Any]:
        """
        Record token usage from an API call.
        
        WHY track each call?
        - Debugging: See which operations use most tokens
        - Billing: Calculate costs per user/feature
        - Optimization: Identify expensive prompts
        
        Args:
            prompt_tokens: Tokens in the request (we pay for these)
            completion_tokens: Tokens in the response (we pay for these too)
            model: Which model was used (affects pricing)
            operation: What we were doing (for logging/analytics)
            
        Returns:
            Dictionary with usage details and estimated cost
        """
        # Update running totals
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_requests += 1
        
        # Calculate estimated cost
        # WHY calculate here? Immediate feedback on API call cost
        # Pricing as of 2024 - check OpenAI's website for current rates
        if "gpt-4" in model:
            cost_per_1k_input = 0.01   # $0.01 per 1K input tokens
            cost_per_1k_output = 0.03  # $0.03 per 1K output tokens
        else:
            cost_per_1k_input = 0.0005   # GPT-3.5 is much cheaper
            cost_per_1k_output = 0.0015
        
        estimated_cost = (
            (prompt_tokens / 1000 * cost_per_1k_input) +
            (completion_tokens / 1000 * cost_per_1k_output)
        )
        
        # Create usage record
        usage_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost_usd": round(estimated_cost, 6)
        }
        
        # Store in history (keep last 100 for memory efficiency)
        self.request_history.append(usage_record)
        if len(self.request_history) > 100:
            self.request_history.pop(0)
        
        # Log the usage
        logger.info(
            f"📊 Token Usage | Operation: {operation} | "
            f"Tokens: {prompt_tokens} + {completion_tokens} = {prompt_tokens + completion_tokens} | "
            f"Cost: ${estimated_cost:.4f}"
        )
        
        return usage_record
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all token usage.
        
        Returns:
            Dictionary with total usage statistics
        """
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": total_tokens,
            "recent_requests": self.request_history[-10:]  # Last 10 requests
        }


# =============================================================================
# MAIN AI SERVICE CLASS
# =============================================================================

class AIService:
    """
    Main AI service for all OpenAI operations.
    
    RESPONSIBILITIES:
    - Initialize and manage OpenAI client
    - Generate resumes from user data
    - Handle errors and retries
    - Track token usage
    
    DESIGN DECISIONS:
    - Async methods: Non-blocking I/O for better performance
    - Instance-based: Each instance has its own usage tracker
    - Lazy initialization: Client created once on first use
    """
    
    def __init__(self):
        """
        Initialize the AI service.
        
        WHAT HAPPENS:
        1. Validates OpenAI API key is configured
        2. Creates OpenAI client with settings from config
        3. Initializes tokenizer for token counting
        4. Sets up usage tracking
        
        RAISES:
            AIConfigurationError: If API key is missing or invalid
        """
        logger.info("=" * 60)
        logger.info("🚀 Initializing AI Service")
        logger.info("=" * 60)
        
        # Step 1: Validate API key
        # WHY validate here? Fail fast - better to crash on startup than on first request
        logger.debug("Step 1: Validating OpenAI API key...")
        
        if not settings.OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY is not set!")
            raise AIConfigurationError(
                "OpenAI API key is not configured. "
                "Please set OPENAI_API_KEY in your .env file. "
                "Get your API key from: https://platform.openai.com/api-keys"
            )
        
        if not settings.OPENAI_API_KEY.startswith("sk-"):
            logger.error("❌ OPENAI_API_KEY format appears invalid")
            raise AIConfigurationError(
                "OpenAI API key appears to be invalid. "
                "Valid keys start with 'sk-'. "
                "Please check your .env file."
            )
        
        # Mask key for logging (show first/last 4 chars only)
        masked_key = f"{settings.OPENAI_API_KEY[:7]}...{settings.OPENAI_API_KEY[-4:]}"
        logger.debug(f"   API Key: {masked_key}")
        logger.info("✅ API key validated")
        
        # Step 2: Create OpenAI client
        # WHY AsyncOpenAI? Allows concurrent requests without blocking
        logger.debug("Step 2: Creating OpenAI client...")
        
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_TIMEOUT,  # Max seconds to wait for response
            max_retries=0  # We handle retries ourselves for more control
        )
        
        logger.info("✅ OpenAI client created")
        
        # Step 3: Store configuration
        logger.debug("Step 3: Loading configuration...")
        
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Max Tokens: {self.max_tokens}")
        logger.info(f"   Temperature: {self.temperature}")
        
        # Step 4: Initialize tokenizer
        # WHY? To count tokens before sending requests
        logger.debug("Step 4: Initializing tokenizer...")
        
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model)
                logger.info(f"✅ Tokenizer initialized for {self.model}")
            except KeyError:
                # Fallback for newer models not in tiktoken
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
                logger.warning(f"⚠️ Using fallback tokenizer (cl100k_base) for {self.model}")
        else:
            self.tokenizer = None
            logger.warning("⚠️ Tiktoken not available, token counting disabled")
        
        # Step 5: Initialize usage tracker
        logger.debug("Step 5: Initializing usage tracker...")
        self.usage_tracker = TokenUsageTracker()
        logger.info("✅ Usage tracker initialized")
        
        logger.info("=" * 60)
        logger.info("🎉 AI Service ready!")
        logger.info("=" * 60)
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        WHY COUNT TOKENS?
        - Prevent exceeding model's context limit (128K for GPT-4 Turbo)
        - Estimate costs before sending request
        - Optimize prompts to reduce costs
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens (estimated if tiktoken not available)
            
        Example:
            >>> ai_service.count_tokens("Hello, world!")
            4
        """
        if self.tokenizer:
            token_count = len(self.tokenizer.encode(text))
        else:
            # Rough estimate: ~4 characters per token
            token_count = len(text) // 4
        logger.debug(f"Token count for {len(text)} characters: {token_count} tokens")
        return token_count
    
    def _create_retry_decorator(self):
        """
        Create a retry decorator with exponential backoff.
        
        WHY EXPONENTIAL BACKOFF?
        - Rate limits: API needs time to reset
        - Server issues: Brief downtime, not permanent failure
        - Prevents hammering the API (which makes things worse)
        
        RETRY SCHEDULE:
        - Attempt 1: Immediate
        - Attempt 2: Wait 1 second
        - Attempt 3: Wait 2 seconds
        - Attempt 4: Wait 4 seconds (if max_retries=4)
        
        Returns:
            Tenacity retry decorator
        """
        return retry(
            # Stop after this many attempts
            stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES),
            
            # Exponential backoff: 1s, 2s, 4s, 8s... up to 10s max
            wait=wait_exponential(multiplier=1, min=1, max=10),
            
            # Only retry on these specific exceptions
            # WHY be specific? Don't retry on auth errors (won't help)
            retry=retry_if_exception_type((RateLimitError, APIError)),
            
            # Log before each retry
            before_sleep=lambda retry_state: logger.warning(
                f"⚠️ API call failed, retrying in {retry_state.next_action.sleep:.1f}s... "
                f"(Attempt {retry_state.attempt_number}/{settings.OPENAI_MAX_RETRIES})"
            )
        )
    
    # =========================================================================
    # MAIN RESUME GENERATION METHOD
    # =========================================================================
    
    async def generate_resume_from_data(
        self,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a professional resume from user-provided data.
        
        This is the PRIMARY method for resume generation. It takes raw user
        data, validates it, constructs a prompt, calls GPT-4, and returns
        a structured resume.
        
        PROCESS:
        1. Validate and parse input data
        2. Build the prompt with user information
        3. Send to OpenAI with retry logic
        4. Parse and validate the response
        5. Return structured resume data
        
        Args:
            input_data: Dictionary containing:
                - name: Full name
                - email: Email address
                - phone: Phone number
                - skills: List of skills
                - experience: List of work experience
                - education: List of education entries
                
        Returns:
            Dictionary containing generated resume with sections:
                - professional_summary
                - contact_info
                - skills (formatted)
                - work_experience (enhanced)
                - education (formatted)
                - metadata (generation info)
        
        Raises:
            AIValidationError: If input data is invalid
            AIGenerationError: If generation fails
            AIRateLimitError: If rate limits exceeded
            
        Example:
            result = await ai_service.generate_resume_from_data({
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "skills": ["Python", "FastAPI"],
                "experience": [...],
                "education": [...]
            })
        """
        logger.info("=" * 60)
        logger.info("📝 Starting Resume Generation")
        logger.info("=" * 60)
        
        start_time = datetime.utcnow()
        
        # =====================================================================
        # STEP 1: Validate and parse input data
        # =====================================================================
        logger.info("Step 1/5: Validating input data...")
        
        try:
            resume_data = ResumeInputData.from_dict(input_data)
            logger.info(f"   ✅ Name: {resume_data.name}")
            logger.info(f"   ✅ Email: {resume_data.email}")
            logger.info(f"   ✅ Skills: {len(resume_data.skills)} skills")
            logger.info(f"   ✅ Experience: {len(resume_data.experience)} entries")
            logger.info(f"   ✅ Education: {len(resume_data.education)} entries")
        except AIValidationError:
            # Re-raise validation errors (already logged)
            raise
        except Exception as e:
            logger.error(f"   ❌ Unexpected validation error: {e}")
            raise AIValidationError(f"Failed to parse input data: {str(e)}")
        
        # =====================================================================
        # STEP 2: Build the prompt
        # =====================================================================
        logger.info("Step 2/5: Building prompt...")
        
        prompt = self._build_resume_prompt(resume_data)
        prompt_tokens = self.count_tokens(prompt)
        
        logger.info(f"   📊 Prompt length: {len(prompt)} characters")
        logger.info(f"   📊 Prompt tokens: {prompt_tokens}")
        
        # Check if prompt is too long
        # WHY? GPT-4 Turbo has 128K context, but we want to leave room for response
        if prompt_tokens > 4000:
            logger.warning(f"   ⚠️ Large prompt detected: {prompt_tokens} tokens")
        
        # =====================================================================
        # STEP 3: Build system message
        # =====================================================================
        logger.info("Step 3/5: Preparing API request...")
        
        system_message = self._get_system_message()
        logger.debug(f"   System message length: {len(system_message)} chars")
        
        # =====================================================================
        # STEP 4: Call OpenAI API
        # =====================================================================
        logger.info("Step 4/5: Calling OpenAI API...")
        logger.info(f"   🤖 Model: {self.model}")
        logger.info(f"   🌡️ Temperature: {self.temperature}")
        logger.info(f"   📏 Max tokens: {self.max_tokens}")
        
        try:
            # Create retry-enabled API call function
            @self._create_retry_decorator()
            async def make_api_call():
                """Make the API call with retry logic."""
                logger.debug("   Making API request...")
                return await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}  # Ensure JSON response
                )
            
            # Execute the API call
            response = await make_api_call()
            logger.info("   ✅ API call successful!")
            
        except RateLimitError as e:
            logger.error(f"   ❌ Rate limit exceeded: {e}")
            raise AIRateLimitError(
                "OpenAI rate limit exceeded. Please wait a moment and try again.",
                details={"error": str(e)}
            )
            
        except AuthenticationError as e:
            logger.error(f"   ❌ Authentication failed: {e}")
            raise AIConfigurationError(
                "OpenAI API key is invalid. Please check your configuration.",
                details={"error": str(e)}
            )
            
        except APIError as e:
            logger.error(f"   ❌ API error: {e}")
            raise AIGenerationError(
                f"OpenAI API error: {str(e)}",
                details={"error": str(e)}
            )
            
        except OpenAIError as e:
            logger.error(f"   ❌ OpenAI error: {e}")
            raise AIGenerationError(
                f"Failed to generate resume: {str(e)}",
                details={"error": str(e)}
            )
        
        # =====================================================================
        # STEP 5: Process and validate response
        # =====================================================================
        logger.info("Step 5/5: Processing response...")
        
        # Track token usage
        usage = response.usage
        self.usage_tracker.add_usage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            model=self.model,
            operation="resume_generation"
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        logger.debug(f"   Response length: {len(response_content)} characters")
        
        # Parse JSON response
        try:
            resume_result = json.loads(response_content)
            logger.info("   ✅ JSON parsed successfully")
        except json.JSONDecodeError as e:
            logger.error(f"   ❌ Failed to parse JSON: {e}")
            logger.debug(f"   Raw response: {response_content[:500]}...")
            raise AIGenerationError(
                "Failed to parse AI response as JSON. Please try again.",
                details={"error": str(e), "response_preview": response_content[:200]}
            )
        
        # Add metadata
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        resume_result["_metadata"] = {
            "generated_at": end_time.isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            "model_used": self.model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
            "input_name": resume_data.name,
            "input_skills_count": len(resume_data.skills),
            "input_experience_count": len(resume_data.experience)
        }
        
        logger.info("=" * 60)
        logger.info("🎉 Resume Generation Complete!")
        logger.info(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
        logger.info(f"   📊 Tokens used: {usage.total_tokens}")
        logger.info("=" * 60)
        
        return resume_result
    
    def _get_system_message(self) -> str:
        """
        Get the system message that defines the AI's role.
        
        WHY A SYSTEM MESSAGE?
        - Establishes context and persona for GPT
        - Sets expectations for output format
        - Improves consistency across requests
        
        Returns:
            System message string
        """
        return """You are an expert professional resume writer with 20+ years of experience.

YOUR ROLE:
- Transform raw candidate data into polished, professional resume content
- Enhance descriptions with strong action verbs and quantifiable achievements
- Ensure ATS (Applicant Tracking System) compatibility
- Make the candidate stand out while remaining truthful

YOUR RULES:
1. ALWAYS return valid JSON matching the specified structure
2. ENHANCE descriptions but don't fabricate information
3. Use strong action verbs (Led, Developed, Achieved, Implemented, etc.)
4. Quantify achievements where possible (e.g., "Improved performance by 40%")
5. Keep content professional and industry-appropriate
6. Ensure ATS-friendly formatting (standard headers, no graphics references)

IMPORTANT:
- Return ONLY valid JSON
- No markdown formatting
- No explanatory text before or after the JSON"""
    
    def _build_resume_prompt(self, data: ResumeInputData) -> str:
        """
        Build the user prompt for resume generation.
        
        WHY A SEPARATE METHOD?
        - Keeps the main method clean
        - Easy to modify prompt structure
        - Testable in isolation
        
        Args:
            data: Validated resume input data
            
        Returns:
            Formatted prompt string
        """
        # Format experience for the prompt
        experience_text = ""
        for i, exp in enumerate(data.experience, 1):
            experience_text += f"""
Experience {i}:
  - Company: {exp.company}
  - Position: {exp.position}
  - Duration: {exp.duration}
  - Description: {exp.description}
"""
        
        # Format education for the prompt
        education_text = ""
        for i, edu in enumerate(data.education, 1):
            education_text += f"""
Education {i}:
  - Institution: {edu.institution}
  - Degree: {edu.degree}
  - Year: {edu.year}
"""
        
        prompt = f"""Generate a professional resume from this candidate data.

CANDIDATE INFORMATION:
======================
Name: {data.name}
Email: {data.email}
Phone: {data.phone}

SKILLS:
=======
{', '.join(data.skills)}

WORK EXPERIENCE:
================
{experience_text}

EDUCATION:
==========
{education_text}

TASK:
=====
Create a polished, professional resume. Enhance the descriptions with strong action verbs
and quantifiable achievements where appropriate. Make the candidate stand out.

OUTPUT FORMAT (JSON):
====================
{{
    "professional_summary": {{
        "text": "A compelling 3-4 sentence professional summary highlighting key strengths and experience",
        "keywords": ["keyword1", "keyword2", "keyword3"]
    }},
    "contact_info": {{
        "name": "{data.name}",
        "email": "{data.email}",
        "phone": "{data.phone}"
    }},
    "skills": {{
        "technical": ["skill1", "skill2"],
        "soft": ["skill1", "skill2"],
        "all_skills": ["all", "skills", "formatted"]
    }},
    "work_experience": [
        {{
            "company": "Company Name",
            "position": "Job Title",
            "duration": "Start - End",
            "highlights": [
                "Achievement or responsibility with strong action verb",
                "Another achievement with metrics if possible"
            ]
        }}
    ],
    "education": [
        {{
            "institution": "Institution Name",
            "degree": "Degree Name",
            "year": "Graduation Year",
            "highlights": ["Any honors, relevant coursework, or achievements"]
        }}
    ]
}}

Return ONLY the JSON. No other text."""
        
        return prompt
    
    # =========================================================================
    # ADDITIONAL AI METHODS
    # =========================================================================
    
    async def generate_resume(
        self,
        job_title: str,
        years_experience: int,
        skills: List[str],
        education_level: str = "Bachelor's",
        field_of_study: Optional[str] = None,
        target_company: Optional[str] = None,
        job_description: Optional[str] = None,
        include_projects: bool = True,
        tone: str = "professional",
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete professional resume.
        
        This is an alternative method that generates a full resume
        from job requirements rather than existing user data.
        """
        logger.info(f"Generating resume for {job_title} with {years_experience} years experience")
        
        # Build prompt for resume generation
        prompt = f"""Generate a complete professional resume for a candidate applying for the position of {job_title}.

CANDIDATE PROFILE:
==================
- Years of Experience: {years_experience}
- Skills: {', '.join(skills)}
- Education Level: {education_level}
{f'- Field of Study: {field_of_study}' if field_of_study else ''}
{f'- Target Company: {target_company}' if target_company else ''}
{f'- Additional Info: {additional_info}' if additional_info else ''}

{f'JOB DESCRIPTION TO MATCH:{chr(10)}{job_description}' if job_description else ''}

REQUIREMENTS:
=============
1. Create realistic work experience entries based on the years of experience
2. Include achievements with quantifiable metrics
3. Match skills to the job requirements
4. Use {tone} tone throughout
5. Make it ATS-friendly
{'6. Include a relevant projects section' if include_projects else ''}

OUTPUT FORMAT (JSON):
====================
{{
    "contact_info": {{
        "name": "Generated Name",
        "email": "email@example.com",
        "phone": "+1 (555) 123-4567",
        "location": "City, Country",
        "linkedin": "linkedin.com/in/username"
    }},
    "professional_summary": {{
        "text": "A compelling 3-4 sentence professional summary",
        "keywords": ["keyword1", "keyword2"]
    }},
    "work_experience": [
        {{
            "company": "Company Name",
            "position": "Job Title",
            "duration": "2022 - Present",
            "location": "City",
            "highlights": [
                "Achievement with metrics",
                "Another achievement"
            ]
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "{education_level}",
            "field": "{field_of_study or 'Related Field'}",
            "year": "Year",
            "honors": ["Honor if any"]
        }}
    ],
    "skills": {{
        "technical": ["technical skills"],
        "soft": ["soft skills"]
    }},
    {"\"projects\": [{\"name\": \"Project Name\", \"description\": \"Description\", \"technologies\": [\"tech1\"]}]," if include_projects else ''}
    "certifications": [
        {{
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "year": "Year"
        }}
    ]
}}

Return ONLY the JSON. No other text."""

        system_message = """You are an expert professional resume writer with 20+ years of experience.
        
YOUR TASK: Generate a realistic, professional resume based on the provided requirements.
YOUR RULES:
1. ALWAYS return valid JSON matching the specified structure
2. Create realistic but fictional work experience
3. Use strong action verbs and quantifiable achievements
4. Make the resume ATS-friendly
5. Tailor content to the target job if provided

IMPORTANT: Return ONLY valid JSON, no markdown or explanatory text."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Track usage
            usage = response.usage
            self.usage_tracker.add_usage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                model=self.model,
                operation="generate_resume"
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Resume generation failed: {e}")
            raise AIGenerationError(f"Failed to generate resume: {str(e)}")
    
    async def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Analyze a resume and provide feedback.
        """
        logger.info("Analyzing resume...")
        
        prompt = f"""Analyze the following resume and provide detailed feedback:

RESUME:
=======
{resume_text}

ANALYSIS REQUIRED:
==================
1. ATS Compatibility Score (0-100)
2. Extract all skills mentioned
3. Identify strengths
4. Identify areas for improvement
5. Specific recommendations

OUTPUT FORMAT (JSON):
====================
{{
    "ats_score": 75,
    "skills_extracted": {{
        "technical": ["skill1", "skill2"],
        "soft": ["skill1", "skill2"]
    }},
    "experience_years_estimated": 5,
    "strengths": [
        "Strength 1 with explanation",
        "Strength 2 with explanation"
    ],
    "weaknesses": [
        "Weakness 1 with explanation"
    ],
    "improvement_suggestions": [
        {{
            "area": "Area to improve",
            "suggestion": "Specific suggestion",
            "priority": "high/medium/low"
        }}
    ],
    "keyword_analysis": {{
        "present": ["keyword1"],
        "missing_recommended": ["keyword2"]
    }},
    "overall_rating": "good/average/needs_improvement",
    "summary": "Brief overall assessment"
}}

Return ONLY the JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and career coach. Provide honest, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Track usage
            self.usage_tracker.add_usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                model=self.model,
                operation="analyze_resume"
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise AIGenerationError(f"Failed to analyze resume: {str(e)}")
    
    async def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        company_name: str,
        hiring_manager: Optional[str] = None,
        tone: str = "professional"
    ) -> str:
        """
        Generate a personalized cover letter.
        """
        logger.info(f"Generating cover letter for {company_name}")
        
        prompt = f"""Generate a compelling cover letter based on:

CANDIDATE'S RESUME:
==================
{resume_text}

JOB DESCRIPTION:
================
{job_description}

COMPANY: {company_name}
{f'HIRING MANAGER: {hiring_manager}' if hiring_manager else ''}
TONE: {tone}

REQUIREMENTS:
=============
1. Match candidate's experience to job requirements
2. Show enthusiasm for the specific company
3. Include specific achievements from resume
4. Keep it concise (3-4 paragraphs)
5. Use {tone} tone

Return ONLY the cover letter text, no JSON or additional formatting."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert cover letter writer. Create compelling, personalized cover letters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Track usage
            self.usage_tracker.add_usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                model=self.model,
                operation="generate_cover_letter"
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            raise AIGenerationError(f"Failed to generate cover letter: {str(e)}")
    
    async def match_resume_to_job(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Analyze how well a resume matches a job description.
        """
        logger.info("Matching resume to job...")
        
        prompt = f"""Analyze how well this resume matches the job description:

RESUME:
=======
{resume_text}

JOB DESCRIPTION:
================
{job_description}

ANALYSIS REQUIRED:
==================
1. Overall match score (0-100)
2. Matching skills and experience
3. Missing skills or qualifications
4. Recommendations for improving match

OUTPUT FORMAT (JSON):
====================
{{
    "match_score": 75,
    "match_level": "good/average/poor",
    "matching_skills": ["skill1", "skill2"],
    "matching_experience": ["relevant experience 1"],
    "missing_skills": ["skill1", "skill2"],
    "missing_qualifications": ["qualification1"],
    "recommendations": [
        {{
            "action": "What to do",
            "reason": "Why it helps",
            "impact": "high/medium/low"
        }}
    ],
    "strengths_for_role": ["strength1"],
    "potential_concerns": ["concern1"],
    "interview_tips": ["tip1", "tip2"],
    "summary": "Brief overall assessment"
}}

Return ONLY the JSON."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR consultant specializing in candidate-job matching."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Track usage
            self.usage_tracker.add_usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                model=self.model,
                operation="match_resume_to_job"
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Job matching failed: {e}")
            raise AIGenerationError(f"Failed to match resume to job: {str(e)}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get a summary of API usage and costs.
        
        Returns:
            Dictionary with usage statistics
        """
        return self.usage_tracker.get_summary()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the AI service is operational.
        
        WHY A HEALTH CHECK?
        - Verify API key works before processing requests
        - Quick status check for monitoring systems
        - Debugging connection issues
        
        Returns:
            Dictionary with health status
        """
        logger.info("Performing AI service health check...")
        
        try:
            # Make a minimal API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            logger.info("✅ Health check passed")
            return {
                "status": "healthy",
                "model": self.model,
                "message": "AI service is operational",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "model": self.model,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_ai_service() -> AIService:
    """
    Factory function to create an AI service instance.
    
    WHY A FACTORY?
    - Dependency injection in FastAPI
    - Easy to mock for testing
    - Centralized instance creation
    
    Returns:
        New AIService instance
        
    Example:
        from fastapi import Depends
        
        @app.post("/generate")
        async def generate(ai: AIService = Depends(create_ai_service)):
            return await ai.generate_resume_from_data(data)
    """
    return AIService()
