# tbh_secure_agents/task.py
# Author: Saish (TBH.AI)

"""
Defines the Operation class for the TBH Secure Agents framework.
Operations represent units of work to be performed by experts.
"""

import logging # Import logging
import re
from typing import Optional, Any
from .agent import Expert # Now we can import Expert

# Get a logger for this module
logger = logging.getLogger(__name__)

class Operation:
    """
    Represents a specific operation to be executed by an expert.

    Attributes:
        instructions (str): A clear description of the operation instructions.
        output_format (str, optional): A description of the expected outcome or format.
        expert (Optional[Expert]): The expert assigned to this operation. Can be assigned later.
        context (Optional[str]): Additional context or data needed for the operation.
        # Add attributes like dependencies, priority, security_requirements, etc.
    """
    def __init__(self, instructions: str, output_format: Optional[str] = None, expert: Optional[Expert] = None, context: Optional[str] = None, **kwargs):
        self.instructions = instructions
        self.output_format = output_format
        self.expert = expert
        self.context = context
        self.result: Optional[str] = None # To store the outcome after execution
        # Initialize other relevant attributes

    def execute(self) -> str:
        """
        Executes the operation, likely by calling the assigned expert's execution method.
        Includes security checks before and after execution.
        """
        if not self.expert:
            logger.error(f"Operation execution failed: No expert assigned to operation '{self.instructions[:50]}...'.") # Use logger
            raise ValueError("Operation cannot be executed without an assigned expert.")

        # Placeholder call, actual logic is in _pre_execution_secure
        logger.debug(f"Performing pre-execution check for operation '{self.instructions[:50]}...'")
        if not self._pre_execution_secure(): # Example placeholder check
            logger.error(f"Operation pre-execution security check failed for '{self.instructions[:50]}...'. Aborting.")
        #     return "Error: Operation failed pre-execution security check."

        logger.info(f"Operation '{self.instructions[:50]}...' starting execution by expert '{self.expert.specialty}'.") # Use logger

        # Assuming the expert has an 'execute_task' method that accepts instructions and context
        try:
            # Pass the operation instructions and any available context to the expert
            self.result = self.expert.execute_task(
                task_description=self.instructions,
                context=self.context # Pass context here
            )
            # Placeholder call, actual logic is in _post_execution_secure
            logger.debug(f"Performing post-execution check for operation '{self.instructions[:50]}...'")
            if not self._post_execution_secure(self.result): # Example placeholder check
                logger.warning(f"Operation post-execution security check failed for '{self.instructions[:50]}...'. Result may be compromised.")
                # TODO: Decide how to handle insecure result (e.g., return error, return sanitized, log only)

            logger.info(f"Operation '{self.instructions[:50]}...' finished execution successfully.")
            return self.result
        except Exception as e:
            # Basic error logging implemented
            logger.error(f"Error executing operation '{self.instructions[:50]}...': {e}", exc_info=True)
            # TODO: Decide whether to raise, return an error string, or handle differently based on policy
            raise # Re-raise for now, allows Squad to handle it

    # --- Placeholder Security Methods ---

    def _pre_execution_secure(self) -> bool:
        """
        Performs security checks before executing an operation.
        Validates the operation instructions, context, and expert assignment to prevent exploitation.

        Returns:
            bool: True if the operation passes all security checks, False otherwise
        """
        logger.debug(f"Performing operation pre-execution check for '{self.instructions[:50]}...'")

        # 1. Check if operation has valid instructions
        if not self.instructions or len(self.instructions.strip()) < 10:
            logger.warning(f"Operation pre-execution security check FAILED: Instructions too short or empty")
            return False

        # 2. Check for excessive instruction length (potential resource exhaustion)
        if len(self.instructions) > 10000:
            logger.warning(f"Operation pre-execution security check FAILED: Instructions too long ({len(self.instructions)} chars)")
            return False

        # 3. Check if expert is properly assigned and has appropriate security profile
        if not self.expert:
            logger.warning(f"Operation pre-execution security check FAILED: No expert assigned")
            return False

        # 4. Check for potentially dangerous operations based on keywords
        dangerous_operation_patterns = [
            r'\b(?:system|exec|eval|subprocess)\s*\(',
            r'\b(?:rm\s+-rf|rmdir\s+/|format\s+[a-z]:)',
            r'\b(?:delete|remove)\s+(?:all|every|database)',
            r'\b(?:drop\s+table|drop\s+database)',
            r'\b(?:wipe|erase)\s+(?:disk|drive|data|database)',
            r'\b(?:hack|crack|exploit)\b',
        ]

        for pattern in dangerous_operation_patterns:
            if re.search(pattern, self.instructions, re.IGNORECASE):
                logger.warning(f"Operation pre-execution security check FAILED: Potentially dangerous operation detected")
                return False

        # 5. Check for operations that might lead to data exfiltration
        data_exfiltration_patterns = [
            r'\b(?:send|transmit|upload|post)\s+(?:data|file|information|content)\s+(?:to|on|at)\s+(?:http|ftp|external)',
            r'\b(?:export|extract|dump)\s+(?:database|data|credentials|secrets)',
            r'\b(?:leak|expose|reveal)\s+(?:data|information|secrets|credentials)',
        ]

        for pattern in data_exfiltration_patterns:
            if re.search(pattern, self.instructions, re.IGNORECASE):
                logger.warning(f"Operation pre-execution security check FAILED: Potential data exfiltration detected")
                return False

        # 6. Check for operations that might lead to privilege escalation
        privilege_escalation_patterns = [
            r'\b(?:sudo|su|runas|administrator|root)\b',
            r'\b(?:escalate|elevate)\s+(?:privilege|permission|access)',
            r'\b(?:gain|obtain)\s+(?:admin|administrator|root)\s+(?:access|privilege|permission)',
        ]

        for pattern in privilege_escalation_patterns:
            if re.search(pattern, self.instructions, re.IGNORECASE):
                logger.warning(f"Operation pre-execution security check FAILED: Potential privilege escalation detected")
                return False

        # 7. Check for operations that might lead to denial of service
        dos_patterns = [
            r'\b(?:infinite|endless|never-ending)\s+(?:loop|recursion|process)',
            r'\b(?:fork\s+bomb|while\s*\(\s*true\s*\))',
            r'\b(?:consume|exhaust)\s+(?:memory|cpu|resource|bandwidth)',
            r'\b(?:overload|flood|overwhelm)\s+(?:server|service|system|network)',
        ]

        for pattern in dos_patterns:
            if re.search(pattern, self.instructions, re.IGNORECASE):
                logger.warning(f"Operation pre-execution security check FAILED: Potential denial of service detected")
                return False

        # 8. Validate that the operation is appropriate for the expert's specialty
        # This is a basic implementation - in a real system, you would have a more sophisticated
        # mapping of operation types to expert specialties
        if hasattr(self.expert, 'specialty') and self.expert.specialty:
            specialty_operation_mismatch = False

            # Example specialty-based validation
            if 'security' in self.expert.specialty.lower() and 'create artwork' in self.instructions.lower():
                specialty_operation_mismatch = True
            elif 'writer' in self.expert.specialty.lower() and 'analyze code' in self.instructions.lower():
                specialty_operation_mismatch = True
            elif 'programmer' in self.expert.specialty.lower() and 'legal advice' in self.instructions.lower():
                specialty_operation_mismatch = True

            if specialty_operation_mismatch:
                logger.warning(f"Operation pre-execution security check FAILED: Operation doesn't match expert specialty")
                return False

        # All checks passed
        logger.debug(f"Operation pre-execution security check PASSED for '{self.instructions[:50]}...'")
        return True

    def _post_execution_secure(self, result: Optional[str]) -> bool:
        """
        Performs security checks on operation results after execution.
        Validates the output for reliability, consistency, and security concerns.

        Args:
            result (Optional[str]): The result of the operation execution

        Returns:
            bool: True if the result passes all security checks, False otherwise
        """
        logger.debug(f"Performing operation post-execution check for '{self.instructions[:50]}...'")

        # 1. Check if result exists
        if not result:
            logger.warning(f"Operation post-execution security check FAILED: Empty result")
            return False

        # 2. Check for excessive result length (potential resource exhaustion)
        if len(result) > 50000:  # Reasonable limit
            logger.warning(f"Operation post-execution security check FAILED: Result too long ({len(result)} chars)")
            return False

        # 3. Check for hallucination indicators
        hallucination_patterns = [
            r"I don't actually (have|know|possess)",
            r"I'm making this up",
            r"I'm not sure (about|if) this is (correct|accurate|right)",
            r"I (can't|cannot) (access|retrieve|find|obtain)",
            r"I don't have (access to|information about)",
            r"(fictional|imaginary|made up) (information|data|details)",
            r"I'm (hallucinating|inventing|creating) this",
        ]

        for pattern in hallucination_patterns:
            if re.search(pattern, result, re.IGNORECASE):
                logger.warning(f"Operation post-execution security check FAILED: Potential hallucination detected")
                return False

        # 4. Check for refusal or inability to complete the operation
        refusal_patterns = [
            r"I (can't|cannot|am unable to) (assist|help|provide|complete|do) (that|this)",
            r"I'm (sorry|afraid) (but|that) I (can't|cannot|am unable to)",
            r"I'm not (able|allowed|permitted) to",
            r"(against|violates) (my|ethical) (guidelines|programming|protocols)",
            r"I (don't|do not) have the (capability|ability|authorization)",
        ]

        for pattern in refusal_patterns:
            if re.search(pattern, result, re.IGNORECASE):
                logger.warning(f"Operation post-execution security check FAILED: Expert refused or was unable to complete operation")
                return False

        # 5. Check for format compliance if output_format is specified
        if self.output_format:
            # Basic format compliance checks based on output_format specification
            if "json" in self.output_format.lower() and not (result.strip().startswith('{') and result.strip().endswith('}')):
                logger.warning(f"Operation post-execution security check FAILED: Result not in expected JSON format")
                return False

            if "list" in self.output_format.lower() and not any(line.strip().startswith(('-', '*', '1.', '2.')) for line in result.split('\n')):
                logger.warning(f"Operation post-execution security check FAILED: Result not in expected list format")
                return False

            if "table" in self.output_format.lower() and not ('|' in result or '\t' in result):
                logger.warning(f"Operation post-execution security check FAILED: Result not in expected table format")
                return False

        # 6. Check for consistency with the operation instructions
        # This is a basic implementation - in a real system, you would have more sophisticated
        # semantic analysis to ensure the result is relevant to the instructions
        key_terms = self._extract_key_terms(self.instructions)
        if key_terms and not any(term.lower() in result.lower() for term in key_terms if len(term) > 4):
            logger.warning(f"Operation post-execution security check FAILED: Result may not be relevant to instructions")
            return False

        # 7. Check for potentially harmful or inappropriate content
        harmful_content_patterns = [
            r'\b(?:bomb|explosive|terrorist|terrorism|attack plan)\b',
            r'\b(?:hack|exploit|vulnerability|attack vector|zero-day)\b',
            r'\b(?:child abuse|child exploitation)\b',
            r'\b(?:genocide|mass shooting|school shooting)\b',
            r'\b(?:suicide|self-harm)\b',
        ]

        for pattern in harmful_content_patterns:
            if re.search(pattern, result, re.IGNORECASE):
                logger.warning(f"Operation post-execution security check FAILED: Potentially harmful content detected")
                return False

        # All checks passed
        logger.debug(f"Operation post-execution security check PASSED for '{self.instructions[:50]}...'")
        return True

    def _extract_key_terms(self, text: str) -> list:
        """
        Extract key terms from text to check for relevance.
        This is a simple implementation that could be enhanced with NLP techniques.

        Args:
            text (str): The text to extract key terms from

        Returns:
            list: A list of key terms
        """
        # Remove common stop words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'from', 'by', 'for',
                     'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above',
                     'below', 'to', 'of', 'in', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
                     'here', 'there', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                     'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
                     'just', 'don', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                     'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
                     'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                     'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
                     'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                     'would', 'should', 'could', 'ought', 'i\'m', 'you\'re', 'he\'s', 'she\'s', 'it\'s', 'we\'re',
                     'they\'re', 'i\'ve', 'you\'ve', 'we\'ve', 'they\'ve', 'i\'d', 'you\'d', 'he\'d', 'she\'d',
                     'we\'d', 'they\'d', 'i\'ll', 'you\'ll', 'he\'ll', 'she\'ll', 'we\'ll', 'they\'ll', 'isn\'t',
                     'aren\'t', 'wasn\'t', 'weren\'t', 'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t', 'don\'t',
                     'didn\'t', 'won\'t', 'wouldn\'t', 'shan\'t', 'shouldn\'t', 'can\'t', 'cannot', 'couldn\'t',
                     'mustn\'t', 'let\'s', 'that\'s', 'who\'s', 'what\'s', 'here\'s', 'there\'s', 'when\'s',
                     'where\'s', 'why\'s', 'how\'s'}

        # Split text into words, convert to lowercase, and filter out stop words and short words
        words = text.lower().split()
        key_terms = [word.strip('.,;:!?()[]{}"\'-') for word in words
                    if word.strip('.,;:!?()[]{}"\'-').lower() not in stop_words
                    and len(word.strip('.,;:!?()[]{}"\'-')) > 3]

        return key_terms

    def __str__(self):
        return f"Operation(instructions='{self.instructions}', expert='{self.expert.specialty if self.expert else 'Unassigned'}')"
