"""Patch engine for applying extensions and modifications to modules."""

import os
import importlib
import importlib.util
import inspect
from typing import Dict, Any, List, Optional, Callable
from .patch_types import Patch, FunctionPatch, ServicePatch, ModelPatch, FieldPatch, RoutePatch


class PatchEngine:
    """
    Engine for loading and applying patches to modules.
    
    The patch engine manages the discovery, loading, and application of patches
    that can modify module behavior at runtime.
    """
    
    def __init__(self):
        """Initialize the patch engine."""
        self.patches: Dict[str, List[Patch]] = {}
        self.logger: Optional[Any] = None
        self.applied_patches: List[str] = []
    
    def set_logger(self, logger):
        """
        Set the logger for the patch engine.
        
        Args:
            logger: Logger instance to use for logging
        """
        self.logger = logger
    
    def load_patches_from_directory(self, directory: str):
        """
        Load all patches from a directory.
        
        Args:
            directory: Directory containing patch files
        """
        if not os.path.exists(directory):
            if self.logger:
                self.logger.log("extensions", f"Patch directory not found: {directory}", "warning")
            return
        
        for filename in os.listdir(directory):
            if (filename.endswith('.py') and 
                not filename.startswith('__') and 
                filename not in ['patch_engine.py', 'patch_types.py']):
                patch_name = filename[:-3]
                try:
                    self._load_patch_file(os.path.join(directory, filename), patch_name)
                except Exception as e:
                    if self.logger:
                        self.logger.log("extensions", f"Failed to load patch {patch_name}: {e}", "error")
    
    def _load_patch_file(self, filepath: str, patch_name: str):
        """
        Load a specific patch file.
        
        Args:
            filepath: Path to the patch file
            patch_name: Name of the patch
        """
        spec = importlib.util.spec_from_file_location(patch_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for patch functions in the module
        if hasattr(module, 'get_patches'):
            patches = module.get_patches()
            self.patches[patch_name] = patches
            if self.logger:
                self.logger.log("extensions", f"Loaded {len(patches)} patches from {patch_name}", "info")
    
    def apply_patches_to_module(self, module_name: str, module_instance: Any, env: Any) -> int:
        """
        Apply all relevant patches to a module.
        
        Args:
            module_name: Name of the module to patch
            module_instance: The module instance to patch
            env: Environment object
            
        Returns:
            Number of patches applied
        """
        applied_count = 0
        
        for patch_name, patches in self.patches.items():
            for patch in patches:
                if self._should_apply_patch(patch, module_name):
                    try:
                        self._apply_patch(patch, module_instance, env)
                        applied_count += 1
                        self.applied_patches.append(f"{patch_name}.{patch.name}")
                        if self.logger:
                            self.logger.log("extensions", f"Applied patch {patch.name} to {module_name}", "info")
                    except Exception as e:
                        if self.logger:
                            self.logger.log("extensions", f"Failed to apply patch {patch.name}: {e}", "error")
        
        return applied_count
    
    def _should_apply_patch(self, patch: Patch, module_name: str) -> bool:
        """
        Check if a patch should be applied to a module.
        
        Args:
            patch: The patch to check
            module_name: Name of the target module
            
        Returns:
            True if patch should be applied
        """
        # Check if patch targets this module
        if hasattr(patch, 'target_module') and patch.target_module != module_name:
            return False
        
        # Check if patch targets all modules
        if hasattr(patch, 'target_module') and patch.target_module == '*':
            return True
        
        return True
    
    def _apply_patch(self, patch: Patch, module_instance: Any, env: Any):
        """
        Apply a single patch to a module instance.
        
        Args:
            patch: The patch to apply
            module_instance: Target module instance
            env: Environment object
        """
        if isinstance(patch, FunctionPatch):
            self._apply_function_patch(patch, module_instance)
        elif isinstance(patch, ServicePatch):
            self._apply_service_patch(patch, module_instance, env)
        elif isinstance(patch, ModelPatch):
            self._apply_model_patch(patch, module_instance)
        elif isinstance(patch, FieldPatch):
            self._apply_field_patch(patch, module_instance)
        elif isinstance(patch, RoutePatch):
            self._apply_route_patch(patch, module_instance, env)
        else:
            # Generic patch application
            if hasattr(patch, 'apply'):
                patch.apply(module_instance, env)
    
    def _apply_function_patch(self, patch: FunctionPatch, module_instance: Any):
        """Apply a function patch."""
        if hasattr(module_instance, patch.function_name):
            setattr(module_instance, patch.function_name, patch.new_function)
    
    def _apply_service_patch(self, patch: ServicePatch, module_instance: Any, env: Any):
        """Apply a service patch."""
        if hasattr(env, 'register_service'):
            env.register_service(patch.service_name, patch.service_instance)
    
    def _apply_model_patch(self, patch: ModelPatch, module_instance: Any):
        """Apply a model patch."""
        if hasattr(module_instance, 'models'):
            setattr(module_instance.models, patch.model_name, patch.new_model)
    
    def _apply_field_patch(self, patch: FieldPatch, module_instance: Any):
        """Apply a field patch."""
        if hasattr(module_instance, patch.model_name):
            model = getattr(module_instance, patch.model_name)
            setattr(model, patch.field_name, patch.new_field)
    
    def _apply_route_patch(self, patch: RoutePatch, module_instance: Any, env: Any):
        """Apply a route patch."""
        if hasattr(env, 'add_route'):
            env.add_route(patch.route_pattern, patch.method, patch.handler, patch.module_name)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded and applied patches.
        
        Returns:
            Dictionary with patch statistics
        """
        return {
            'total_patches': sum(len(patches) for patches in self.patches.values()),
            'patch_files': len(self.patches),
            'applied_patches': len(self.applied_patches),
            'applied_patch_list': self.applied_patches.copy()
        }
    
    def list_patches(self) -> Dict[str, List[str]]:
        """
        List all available patches by file.
        
        Returns:
            Dictionary mapping patch file names to patch names
        """
        result = {}
        for patch_name, patches in self.patches.items():
            result[patch_name] = [patch.name for patch in patches]
        return result
