# tbh_secure_agents/crew.py
# Author: Saish (TBH.AI)

"""
Defines the Squad class for the TBH Secure Agents framework.
A Squad manages a collection of experts and orchestrates the execution of operations.
"""

import logging # Import logging
import time
import re
from typing import List, Optional, Dict, Any
from .agent import Expert # Import Expert class
from .task import Operation # Import Operation class

# Get a logger for this module
logger = logging.getLogger(__name__)

class Squad:
    """
    Manages a group of experts and orchestrates the execution of a sequence of operations.

    Attributes:
        experts (List[Expert]): A list of Expert objects part of this squad.
        operations (List[Operation]): A list of Operation objects to be executed by the squad.
        process (str): The execution process ('sequential', 'hierarchical', etc.). Defaults to 'sequential'.
        # Add attributes like memory, security_manager, etc.
    """
    def __init__(self, experts: List[Expert], operations: List[Operation], process: str = 'sequential', **kwargs):
        self.experts = experts
        self.operations = operations
        self.process = process # Example: 'sequential', 'hierarchical'
        # TODO: Implement initialization of security manager/context for the squad
        # TODO: Implement validation of expert compatibility and operation assignments based on security profiles

        if not experts:
            raise ValueError("Squad must have at least one expert.")
        if not operations:
            logger.error("Squad initialization failed: Must have at least one operation.") # Use logger
            raise ValueError("Squad must have at least one operation.")

        logger.info(f"Squad initialized with {len(self.experts)} experts and {len(self.operations)} operations. Process: {self.process}") # Use logger

    def deploy(self) -> Optional[str]:
        """
        Starts the execution of the operations by the experts in the squad.
        Includes security checks and orchestration controls to prevent exploitation.

        Returns:
            Optional[str]: The final output of the squad's execution, or None if there's no final output or an error occurred.
        """
        logger.info("Squad deployment initiated...")

        # Security check: Validate squad configuration before execution
        if not self._validate_squad_security():
            logger.error("Squad deployment aborted: Security validation failed")
            return "Error: Squad security validation failed. Deployment aborted."

        # Initialize execution tracking
        final_output: Optional[str] = None
        # Store outputs to potentially pass as context to next operations
        # Key: Operation instructions (or a unique operation ID), Value: Operation result
        operation_outputs: Dict[str, str] = {}

        # Track execution metrics for security monitoring
        self.execution_metrics = {
            'start_time': time.time(),
            'operations_completed': 0,
            'operations_failed': 0,
            'total_operations': len(self.operations),
            'execution_path': []
        }

        for i, operation in enumerate(self.operations):
            # Record operation in execution path for auditing
            operation_record = {
                'index': i,
                'instructions': operation.instructions[:100] + ('...' if len(operation.instructions) > 100 else ''),
                'start_time': time.time(),
                'status': 'pending'
            }
            self.execution_metrics['execution_path'].append(operation_record)

            # Security check: Validate operation before assignment
            logger.debug(f"Validating operation {i+1}/{len(self.operations)}: '{operation.instructions[:30]}...'")
            if not self._validate_operation_security(operation, i):
                logger.error(f"Operation validation failed for operation {i+1}: '{operation.instructions[:30]}...'")
                operation_record['status'] = 'validation_failed'
                self.execution_metrics['operations_failed'] += 1
                if self.process == 'sequential':
                    return f"Squad execution failed: Security validation failed for operation {i+1}"
                else:
                    continue  # Skip this operation but continue with others for non-sequential processes

            # Assign expert if not already assigned
            if not operation.expert:
                # Implement more sophisticated expert assignment logic based on specialty matching
                best_expert = self._find_best_expert_for_operation(operation)
                if best_expert:
                    operation.expert = best_expert
                    logger.info(f"Assigning Operation '{operation.instructions[:30]}...' to Expert '{best_expert.specialty}'")
                else:
                    # Fallback to simple assignment if no good match
                    assigned_expert = self.experts[i % len(self.experts)]
                    operation.expert = assigned_expert
                    logger.info(f"Assigning Operation '{operation.instructions[:30]}...' to Expert '{assigned_expert.specialty}' (default assignment)")
            else: # Expert was pre-assigned
                logger.info(f"Operation '{operation.instructions[:30]}...' already assigned to Expert '{operation.expert.specialty}'")

            # --- Context Passing with Security Checks ---
            if i > 0 and self.process == 'sequential':
                previous_operation = self.operations[i-1]
                if previous_operation.result:
                    # Check if previous result is safe to pass as context
                    if self._is_safe_for_context_passing(previous_operation.result, operation):
                        # Securely format and append previous result to current context
                        new_context = f"Output from previous operation ({previous_operation.instructions[:30]}...): {previous_operation.result}"
                        if operation.context:
                            operation.context += f"\n\n{new_context}"
                        else:
                            operation.context = new_context
                        logger.debug(f"Injecting context from previous operation into Operation '{operation.instructions[:30]}...'")
                    else:
                        logger.warning(f"Context passing blocked: Previous result deemed unsafe for operation '{operation.instructions[:30]}...'")

            # Set operation timeout for safety
            operation_timeout = self._calculate_operation_timeout(operation)
            operation_start_time = time.time()

            try:
                # Execute the operation with timeout monitoring
                logger.info(f"Executing operation {i+1}/{len(self.operations)}: '{operation.instructions[:30]}...'")

                # Execute the operation
                output = operation.execute()

                # Check execution time
                execution_time = time.time() - operation_start_time
                if execution_time > operation_timeout:
                    logger.warning(f"Operation took longer than expected: {execution_time:.2f}s > {operation_timeout:.2f}s")

                # Update operation record
                operation_record['end_time'] = time.time()
                operation_record['execution_time'] = operation_record['end_time'] - operation_record['start_time']

                if output: # Store output only if execution was successful
                    # Perform additional security check on output
                    if self._is_output_safe(output, operation):
                        operation_outputs[operation.instructions] = output
                        final_output = output # Keep track of the last output as the final one (for sequential)
                        operation_record['status'] = 'completed'
                        self.execution_metrics['operations_completed'] += 1
                        logger.info(f"Operation {i+1} completed successfully in {operation_record['execution_time']:.2f}s")
                    else:
                        operation_record['status'] = 'unsafe_output'
                        self.execution_metrics['operations_failed'] += 1
                        logger.error(f"Operation {i+1} produced unsafe output")
                        if self.process == 'sequential':
                            return f"Squad execution failed: Operation {i+1} produced unsafe output"
                else:
                    operation_record['status'] = 'empty_output'
                    logger.warning(f"Operation {i+1} produced empty output")

            except Exception as e:
                # Update operation record
                operation_record['end_time'] = time.time()
                operation_record['execution_time'] = operation_record['end_time'] - operation_record['start_time']
                operation_record['status'] = 'failed'
                operation_record['error'] = str(e)

                # Update metrics
                self.execution_metrics['operations_failed'] += 1

                # Log error
                logger.error(f"Squad execution failed during operation {i+1}: '{operation.instructions[:50]}...': {e}", exc_info=True)

                # Handle failure based on process type
                if self.process == 'sequential':
                    return f"Squad execution failed: Error during operation {i+1}: '{operation.instructions[:50]}...'"
                # For non-sequential processes, we might continue with other operations

        # Update execution metrics
        self.execution_metrics['end_time'] = time.time()
        self.execution_metrics['total_execution_time'] = self.execution_metrics['end_time'] - self.execution_metrics['start_time']

        # Log execution metrics for security monitoring
        logger.info(f"Squad deployment finished. Execution time: {self.execution_metrics['total_execution_time']:.2f}s, "
                   f"Operations completed: {self.execution_metrics['operations_completed']}, "
                   f"Operations failed: {self.execution_metrics['operations_failed']}")

        # Perform final security audit on results
        if not self._audit_squad_results(final_output):
            logger.warning("Final squad result audit failed. Results may be compromised.")
            return "Error: Squad result audit failed. Results may be compromised."

        return final_output

    def _validate_squad_security(self) -> bool:
        """
        Validates the security of the squad configuration before execution.
        Checks for potential security issues in the squad setup.

        Returns:
            bool: True if the squad passes all security checks, False otherwise
        """
        logger.debug("Validating squad security...")

        # 1. Check if there are any experts and operations
        if not self.experts:
            logger.error("Squad security validation failed: No experts in squad")
            return False

        if not self.operations:
            logger.error("Squad security validation failed: No operations in squad")
            return False

        # 2. Check for expert security profiles
        security_profiles = [expert.security_profile for expert in self.experts if hasattr(expert, 'security_profile')]
        if not security_profiles or any(not profile for profile in security_profiles):
            logger.warning("Squad security validation: Some experts have no security profile")
            # Warning only, not a failure

        # 3. Check for potential circular dependencies or infinite loops in operations
        # This is a simplified check - in a real system, you would have more sophisticated
        # dependency analysis
        if self.process == 'sequential' and len(self.operations) > 20:
            logger.warning("Squad security validation: Large number of sequential operations may indicate inefficiency")
            # Warning only, not a failure

        # 4. Check for expert-operation compatibility
        for operation in self.operations:
            if operation.expert and not hasattr(operation.expert, 'execute_task'):
                logger.error(f"Squad security validation failed: Expert assigned to operation '{operation.instructions[:30]}...' lacks execute_task method")
                return False

        # 5. Check for duplicate operations (potential redundancy attack)
        operation_instructions = [operation.instructions for operation in self.operations]
        if len(operation_instructions) != len(set(operation_instructions)):
            logger.warning("Squad security validation: Duplicate operation instructions detected")
            # Warning only, not a failure

        # 6. Check for excessive resource usage
        total_instruction_length = sum(len(operation.instructions) for operation in self.operations)
        if total_instruction_length > 100000:  # Arbitrary limit
            logger.error(f"Squad security validation failed: Total operation instructions too long ({total_instruction_length} chars)")
            return False

        # 7. Check for proper process type
        valid_processes = ['sequential', 'hierarchical', 'parallel']
        if self.process not in valid_processes:
            logger.error(f"Squad security validation failed: Invalid process type '{self.process}'")
            return False

        # All checks passed
        logger.debug("Squad security validation passed")
        return True

    def _audit_squad_results(self, final_output: Optional[str]) -> bool:
        """
        Performs a security audit on the final results of the squad execution.

        Args:
            final_output (Optional[str]): The final output of the squad execution

        Returns:
            bool: True if the results pass all security checks, False otherwise
        """
        logger.debug("Performing squad result audit...")

        # 1. Check if there is a final output
        if not final_output:
            logger.warning("Squad result audit: No final output")
            return True  # Not necessarily a failure

        # 2. Check for excessive output length
        if len(final_output) > 100000:  # Arbitrary limit
            logger.warning("Squad result audit failed: Final output too long")
            return False

        # 3. Check execution metrics for anomalies
        if hasattr(self, 'execution_metrics'):
            # Check for operations that took too long
            if self.execution_metrics.get('total_execution_time', 0) > 300:  # 5 minutes
                logger.warning("Squad result audit: Execution took unusually long")
                # Warning only, not a failure

            # Check for failed operations
            if self.execution_metrics.get('operations_failed', 0) > 0:
                logger.warning(f"Squad result audit: {self.execution_metrics.get('operations_failed')} operations failed")
                # Warning only, not a failure

            # Check for completion rate
            completed = self.execution_metrics.get('operations_completed', 0)
            total = self.execution_metrics.get('total_operations', 0)
            if total > 0 and completed / total < 0.5:
                logger.warning(f"Squad result audit: Low operation completion rate ({completed}/{total})")
                # Warning only, not a failure

        # 4. Check for potentially harmful content in the final output
        harmful_content_patterns = [
            r'\b(?:bomb|explosive|terrorist|terrorism|attack plan)\b',
            r'\b(?:hack|exploit|vulnerability|attack vector|zero-day)\b',
            r'\b(?:child abuse|child exploitation)\b',
            r'\b(?:genocide|mass shooting|school shooting)\b',
            r'\b(?:suicide|self-harm)\b',
        ]

        for pattern in harmful_content_patterns:
            if re.search(pattern, final_output, re.IGNORECASE):
                logger.warning("Squad result audit failed: Potentially harmful content detected in final output")
                return False

        # All checks passed
        logger.debug("Squad result audit passed")
        return True

    def _validate_operation_security(self, operation: Operation, index: int) -> bool:
        """
        Validates the security of an operation before execution.

        Args:
            operation (Operation): The operation to validate
            index (int): The index of the operation in the task list

        Returns:
            bool: True if the operation passes all security checks, False otherwise
        """
        # 1. Check if operation has valid instructions
        if not operation.instructions or len(operation.instructions.strip()) < 10:
            logger.error(f"Operation security validation failed: Instructions too short or empty")
            return False

        # 2. Check for excessive instruction length
        if len(operation.instructions) > 10000:
            logger.error(f"Operation security validation failed: Instructions too long ({len(operation.instructions)} chars)")
            return False

        # 3. Check for potentially dangerous operations based on keywords
        dangerous_patterns = [
            r'\b(?:system|exec|eval|subprocess)\s*\(',
            r'\b(?:rm\s+-rf|rmdir\s+/|format\s+[a-z]:)',
            r'\b(?:delete|remove)\s+(?:all|every|database)',
            r'\b(?:drop\s+table|drop\s+database)',
            r'\b(?:wipe|erase)\s+(?:disk|drive|data|database)',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, operation.instructions, re.IGNORECASE):
                logger.error(f"Operation security validation failed: Potentially dangerous operation detected")
                return False

        # 4. Check for operations that might lead to data exfiltration
        if re.search(r'\b(?:send|transmit|upload|post)\s+(?:data|file|information|content)\s+(?:to|on|at)\s+(?:http|ftp|external)',
                    operation.instructions, re.IGNORECASE):
            logger.error(f"Operation security validation failed: Potential data exfiltration detected")
            return False

        # All checks passed
        return True

    def _find_best_expert_for_operation(self, operation: Operation) -> Optional[Expert]:
        """
        Finds the best expert for an operation based on specialty matching.

        Args:
            operation (Operation): The operation to find an expert for

        Returns:
            Optional[Expert]: The best matching expert, or None if no good match is found
        """
        if not self.experts:
            return None

        # Simple keyword matching between operation instructions and expert specialty
        # In a real system, you would use more sophisticated matching algorithms
        best_match = None
        best_score = 0

        for expert in self.experts:
            if not hasattr(expert, 'specialty') or not expert.specialty:
                continue

            # Calculate a simple match score based on word overlap
            expert_words = set(expert.specialty.lower().split())
            instruction_words = set(operation.instructions.lower().split())

            # Calculate intersection of words
            common_words = expert_words.intersection(instruction_words)
            score = len(common_words)

            # Bonus for security profile match if operation has security requirements
            if hasattr(expert, 'security_profile') and expert.security_profile:
                if 'secure' in operation.instructions.lower() and 'high' in expert.security_profile.lower():
                    score += 2

            if score > best_score:
                best_score = score
                best_match = expert

        # Only return if we have a reasonable match
        if best_score > 0:
            return best_match

        return None

    def _is_safe_for_context_passing(self, previous_result: str, next_operation: Operation) -> bool:
        """
        Checks if a previous operation's result is safe to pass as context to the next operation.

        Args:
            previous_result (str): The result of the previous operation
            next_operation (Operation): The next operation to receive the context

        Returns:
            bool: True if the result is safe to pass as context, False otherwise
        """
        # 1. Check for excessive length
        if len(previous_result) > 50000:
            logger.warning("Context passing check: Previous result too long")
            return False

        # 2. Check for potentially harmful content
        harmful_patterns = [
            r'\b(?:bomb|explosive|terrorist|terrorism|attack plan)\b',
            r'\b(?:hack|exploit|vulnerability|attack vector|zero-day)\b',
            r'\b(?:child abuse|child exploitation)\b',
            r'\b(?:genocide|mass shooting|school shooting)\b',
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, previous_result, re.IGNORECASE):
                logger.warning("Context passing check: Potentially harmful content detected")
                return False

        # 3. Check for potential prompt injection attempts in the previous result
        injection_patterns = [
            r"ignore (previous|prior|above) instructions",
            r"disregard (previous|prior|above) instructions",
            r"forget (previous|prior|above) instructions",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, previous_result, re.IGNORECASE):
                logger.warning("Context passing check: Potential prompt injection detected")
                return False

        # All checks passed
        return True

    def _calculate_operation_timeout(self, operation: Operation) -> float:
        """
        Calculates an appropriate timeout for an operation based on its complexity.

        Args:
            operation (Operation): The operation to calculate a timeout for

        Returns:
            float: The timeout in seconds
        """
        # Base timeout
        timeout = 30.0  # 30 seconds base timeout

        # Adjust based on instruction length (proxy for complexity)
        instruction_length = len(operation.instructions)
        if instruction_length > 1000:
            timeout += min(30, instruction_length / 100)  # Add up to 30 seconds based on length

        # Adjust based on operation type (if we can infer it from instructions)
        if re.search(r'\b(?:analyze|research|investigate|study)\b', operation.instructions, re.IGNORECASE):
            timeout += 30  # Research operations may take longer

        if re.search(r'\b(?:generate|create|write|draft)\b', operation.instructions, re.IGNORECASE):
            timeout += 20  # Creative operations may take longer

        if re.search(r'\b(?:summarize|condense|shorten)\b', operation.instructions, re.IGNORECASE):
            timeout += 10  # Summarization operations may take a bit longer

        # Cap the timeout at a reasonable maximum
        max_timeout = 180  # 3 minutes maximum
        return min(timeout, max_timeout)

    def _is_output_safe(self, output: str, operation: Operation) -> bool:
        """
        Checks if an operation's output is safe.

        Args:
            output (str): The output to check
            operation (Operation): The operation that produced the output

        Returns:
            bool: True if the output is safe, False otherwise
        """
        # 1. Check for excessive length
        if len(output) > 50000:
            logger.warning("Output safety check: Output too long")
            return False

        # 2. Check for potentially harmful content
        harmful_patterns = [
            r'\b(?:bomb|explosive|terrorist|terrorism|attack plan)\b',
            r'\b(?:hack|exploit|vulnerability|attack vector|zero-day)\b',
            r'\b(?:child abuse|child exploitation)\b',
            r'\b(?:genocide|mass shooting|school shooting)\b',
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                logger.warning("Output safety check: Potentially harmful content detected")
                return False

        # 3. Check for hallucination indicators
        hallucination_patterns = [
            r"I don't actually (have|know|possess)",
            r"I'm making this up",
            r"I'm not sure (about|if) this is (correct|accurate|right)",
            r"I (can't|cannot) (access|retrieve|find|obtain)",
        ]

        for pattern in hallucination_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                logger.warning("Output safety check: Potential hallucination detected")
                return False

        # 4. Check for refusal or inability to complete the operation
        refusal_patterns = [
            r"I (can't|cannot|am unable to) (assist|help|provide|complete|do) (that|this)",
            r"I'm (sorry|afraid) (but|that) I (can't|cannot|am unable to)",
            r"I'm not (able|allowed|permitted) to",
        ]

        for pattern in refusal_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                logger.warning("Output safety check: Expert refused or was unable to complete operation")
                return False

        # All checks passed
        return True
